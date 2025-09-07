<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class ComplianceChecker extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->checkCompliance($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function checkCompliance(string $url): array
    {
        try {
            $checks = [];
            $totalScore = 0.0;
            $maxScore = 0.0;

            // Check terms of service
            $termsCheck = $this->checkTermsOfService($url);
            $checks[] = $termsCheck;
            $totalScore += $termsCheck['score'];
            $maxScore += 1.0;

            // Check cookie compliance
            $cookieCheck = $this->checkCookieCompliance($url);
            $checks[] = $cookieCheck;
            $totalScore += $cookieCheck['score'];
            $maxScore += 1.0;

            // Check accessibility compliance
            $accessibilityCheck = $this->checkAccessibilityCompliance($url);
            $checks[] = $accessibilityCheck;
            $totalScore += $accessibilityCheck['score'];
            $maxScore += 1.0;

            // Check legal notices
            $legalCheck = $this->checkLegalNotices($url);
            $checks[] = $legalCheck;
            $totalScore += $legalCheck['score'];
            $maxScore += 1.0;

            // Check data protection compliance
            $dataProtectionCheck = $this->checkDataProtectionCompliance($url);
            $checks[] = $dataProtectionCheck;
            $totalScore += $dataProtectionCheck['score'];
            $maxScore += 1.0;

            $finalScore = $maxScore > 0 ? $totalScore / $maxScore : 0.0;

            return [
                'score' => $finalScore,
                'details' => [
                    'url' => $url,
                    'checks' => $checks,
                    'total_checks' => count($checks),
                    'passed_checks' => count(array_filter($checks, fn($c) => $c['passed']))
                ]
            ];

        } catch (Exception $e) {
            return [
                'score' => 0.0,
                'details' => [
                    'error' => $e->getMessage(),
                    'url' => $url,
                    'checks' => []
                ]
            ];
        }
    }

    private function checkTermsOfService(string $url): array
    {
        try {
            $termsUrls = $this->findTermsOfServiceUrls($url);
            
            if (empty($termsUrls)) {
                return [
                    'name' => 'Terms of Service',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No terms of service found',
                    'urls_checked' => []
                ];
            }

            // Check if any terms page is accessible
            $accessibleUrls = [];
            foreach ($termsUrls as $termsUrl) {
                if ($this->isUrlAccessible($termsUrl)) {
                    $accessibleUrls[] = $termsUrl;
                }
            }

            if (empty($accessibleUrls)) {
                return [
                    'name' => 'Terms of Service',
                    'passed' => false,
                    'score' => 0.3,
                    'message' => 'Terms of service found but not accessible',
                    'urls_checked' => $termsUrls
                ];
            }

            // Check content quality
            $contentQuality = $this->checkTermsContentQuality($accessibleUrls[0]);
            $score = $contentQuality['score'];

            return [
                'name' => 'Terms of Service',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => 'Terms of service found and accessible',
                'urls_checked' => $termsUrls,
                'accessible_urls' => $accessibleUrls,
                'content_quality' => $contentQuality
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Terms of Service',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Terms of service check failed: ' . $e->getMessage(),
                'urls_checked' => []
            ];
        }
    }

    private function checkCookieCompliance(string $url): array
    {
        try {
            $content = $this->fetchUrlContent($url);
            
            $score = 0.0;
            $complianceFactors = [];

            // Check for cookie banner/notice
            $cookieKeywords = ['cookie', 'cookies', 'tracking', 'privacy', 'consent'];
            $cookieFound = false;
            
            foreach ($cookieKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $cookieFound = true;
                    break;
                }
            }

            if ($cookieFound) {
                $score += 0.3;
                $complianceFactors[] = 'Cookie-related content found';
            }

            // Check for cookie policy link
            if (preg_match('/<a[^>]+href=["\']([^"\']*cookie[^"\']*)["\'][^>]*>/i', $content)) {
                $score += 0.3;
                $complianceFactors[] = 'Cookie policy link found';
            }

            // Check for consent mechanism
            $consentKeywords = ['accept', 'consent', 'agree', 'opt-in', 'opt-out'];
            $consentFound = false;
            
            foreach ($consentKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $consentFound = true;
                    break;
                }
            }

            if ($consentFound) {
                $score += 0.2;
                $complianceFactors[] = 'Consent mechanism found';
            }

            // Check for GDPR cookie compliance
            $gdprKeywords = ['gdpr', 'general data protection regulation', 'data protection'];
            $gdprFound = false;
            
            foreach ($gdprKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $gdprFound = true;
                    break;
                }
            }

            if ($gdprFound) {
                $score += 0.2;
                $complianceFactors[] = 'GDPR compliance mentioned';
            }

            $score = min($score, 1.0);

            return [
                'name' => 'Cookie Compliance',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => empty($complianceFactors) ? 'No cookie compliance indicators found' : implode(', ', $complianceFactors),
                'compliance_factors' => $complianceFactors
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Cookie Compliance',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Cookie compliance check failed: ' . $e->getMessage(),
                'compliance_factors' => []
            ];
        }
    }

    private function checkAccessibilityCompliance(string $url): array
    {
        try {
            $content = $this->fetchUrlContent($url);
            
            $score = 0.0;
            $accessibilityFactors = [];

            // Check for alt attributes on images
            preg_match_all('/<img[^>]*>/i', $content, $imgMatches);
            $totalImages = count($imgMatches[0]);
            $imagesWithAlt = 0;
            
            foreach ($imgMatches[0] as $imgTag) {
                if (str_contains($imgTag, 'alt=')) {
                    $imagesWithAlt++;
                }
            }
            
            if ($totalImages > 0) {
                $altRatio = $imagesWithAlt / $totalImages;
                $score += $altRatio * 0.3;
                $accessibilityFactors[] = "Images with alt text: $imagesWithAlt/$totalImages";
            }

            // Check for heading structure
            preg_match_all('/<h[1-6][^>]*>/i', $content, $headingMatches);
            $totalHeadings = count($headingMatches[0]);
            
            if ($totalHeadings > 0) {
                $score += 0.2;
                $accessibilityFactors[] = "Headings found: $totalHeadings";
            }

            // Check for form labels
            preg_match_all('/<input[^>]*>/i', $content, $inputMatches);
            $totalInputs = count($inputMatches[0]);
            $inputsWithLabels = 0;
            
            foreach ($inputMatches[0] as $inputTag) {
                if (str_contains($inputTag, 'aria-label=') || str_contains($inputTag, 'title=')) {
                    $inputsWithLabels++;
                }
            }
            
            if ($totalInputs > 0) {
                $labelRatio = $inputsWithLabels / $totalInputs;
                $score += $labelRatio * 0.2;
                $accessibilityFactors[] = "Inputs with labels: $inputsWithLabels/$totalInputs";
            }

            // Check for skip links
            if (preg_match('/<a[^>]*href=["\']#(?:main|content|skip)["\'][^>]*>/i', $content)) {
                $score += 0.1;
                $accessibilityFactors[] = 'Skip links found';
            }

            // Check for ARIA attributes
            if (preg_match('/aria-[a-z-]+=/i', $content)) {
                $score += 0.1;
                $accessibilityFactors[] = 'ARIA attributes found';
            }

            // Check for language declaration
            if (preg_match('/<html[^>]*lang=["\']([^"\']+)["\'][^>]*>/i', $content)) {
                $score += 0.1;
                $accessibilityFactors[] = 'Language declaration found';
            }

            $score = min($score, 1.0);

            return [
                'name' => 'Accessibility Compliance',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => empty($accessibilityFactors) ? 'No accessibility features found' : implode(', ', $accessibilityFactors),
                'accessibility_factors' => $accessibilityFactors
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Accessibility Compliance',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Accessibility check failed: ' . $e->getMessage(),
                'accessibility_factors' => []
            ];
        }
    }

    private function checkLegalNotices(string $url): array
    {
        try {
            $legalUrls = $this->findLegalNoticeUrls($url);
            
            if (empty($legalUrls)) {
                return [
                    'name' => 'Legal Notices',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No legal notices found',
                    'urls_checked' => []
                ];
            }

            // Check if any legal page is accessible
            $accessibleUrls = [];
            foreach ($legalUrls as $legalUrl) {
                if ($this->isUrlAccessible($legalUrl)) {
                    $accessibleUrls[] = $legalUrl;
                }
            }

            if (empty($accessibleUrls)) {
                return [
                    'name' => 'Legal Notices',
                    'passed' => false,
                    'score' => 0.3,
                    'message' => 'Legal notices found but not accessible',
                    'urls_checked' => $legalUrls
                ];
            }

            // Check content quality
            $contentQuality = $this->checkLegalContentQuality($accessibleUrls[0]);
            $score = $contentQuality['score'];

            return [
                'name' => 'Legal Notices',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => 'Legal notices found and accessible',
                'urls_checked' => $legalUrls,
                'accessible_urls' => $accessibleUrls,
                'content_quality' => $contentQuality
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Legal Notices',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Legal notices check failed: ' . $e->getMessage(),
                'urls_checked' => []
            ];
        }
    }

    private function checkDataProtectionCompliance(string $url): array
    {
        try {
            $content = $this->fetchUrlContent($url);
            
            $score = 0.0;
            $complianceFactors = [];

            // Check for data protection keywords
            $dataProtectionKeywords = [
                'data protection', 'personal data', 'data processing', 'data controller',
                'data processor', 'data subject', 'consent', 'lawful basis',
                'legitimate interest', 'data minimization', 'purpose limitation',
                'storage limitation', 'accuracy', 'integrity', 'confidentiality'
            ];

            $foundKeywords = [];
            foreach ($dataProtectionKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $foundKeywords[] = $keyword;
                    $score += 0.1;
                }
            }

            if (!empty($foundKeywords)) {
                $complianceFactors[] = 'Data protection keywords found: ' . count($foundKeywords);
            }

            // Check for privacy policy link
            if (preg_match('/<a[^>]+href=["\']([^"\']*privacy[^"\']*)["\'][^>]*>/i', $content)) {
                $score += 0.2;
                $complianceFactors[] = 'Privacy policy link found';
            }

            // Check for data protection officer contact
            $dpoKeywords = ['data protection officer', 'dpo', 'privacy officer'];
            foreach ($dpoKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $score += 0.2;
                    $complianceFactors[] = 'Data protection officer mentioned';
                    break;
                }
            }

            // Check for data retention policy
            $retentionKeywords = ['retention', 'retain', 'delete', 'remove', 'purge'];
            foreach ($retentionKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $score += 0.1;
                    $complianceFactors[] = 'Data retention policy mentioned';
                    break;
                }
            }

            $score = min($score, 1.0);

            return [
                'name' => 'Data Protection Compliance',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => empty($complianceFactors) ? 'No data protection compliance indicators found' : implode(', ', $complianceFactors),
                'compliance_factors' => $complianceFactors
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Data Protection Compliance',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Data protection compliance check failed: ' . $e->getMessage(),
                'compliance_factors' => []
            ];
        }
    }

    private function findTermsOfServiceUrls(string $url): array
    {
        $termsUrls = [];
        $baseUrl = $this->getBaseUrl($url);
        
        // Common terms of service URL patterns
        $termsPaths = [
            '/terms',
            '/terms-of-service',
            '/terms_of_service',
            '/terms.html',
            '/terms.php',
            '/legal/terms',
            '/about/terms',
            '/tos',
            '/terms-and-conditions'
        ];

        foreach ($termsPaths as $path) {
            $termsUrls[] = $baseUrl . $path;
        }

        // Try to find terms links on the main page
        try {
            $content = $this->fetchUrlContent($url);
            $termsLinks = $this->extractTermsLinks($content, $baseUrl);
            $termsUrls = array_merge($termsUrls, $termsLinks);
        } catch (Exception $e) {
            // Ignore errors when fetching main page
        }

        return array_unique($termsUrls);
    }

    private function findLegalNoticeUrls(string $url): array
    {
        $legalUrls = [];
        $baseUrl = $this->getBaseUrl($url);
        
        // Common legal notice URL patterns
        $legalPaths = [
            '/legal',
            '/legal-notice',
            '/legal_notice',
            '/legal.html',
            '/legal.php',
            '/about/legal',
            '/disclaimer',
            '/imprint'
        ];

        foreach ($legalPaths as $path) {
            $legalUrls[] = $baseUrl . $path;
        }

        return array_unique($legalUrls);
    }

    private function extractTermsLinks(string $content, string $baseUrl): array
    {
        $links = [];
        
        // Look for links containing terms-related keywords
        $termsKeywords = ['terms', 'service', 'agreement', 'conditions', 'legal'];
        
        preg_match_all('/<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<\/a>/i', $content, $matches);
        
        foreach ($matches[1] as $href) {
            $hrefLower = strtolower($href);
            foreach ($termsKeywords as $keyword) {
                if (str_contains($hrefLower, $keyword)) {
                    $fullUrl = $this->resolveUrl($href, $baseUrl);
                    if ($fullUrl) {
                        $links[] = $fullUrl;
                    }
                    break;
                }
            }
        }

        return $links;
    }

    private function checkTermsContentQuality(string $url): array
    {
        try {
            $content = $this->fetchUrlContent($url);
            $score = 0.0;
            $qualityFactors = [];

            // Check content length
            $contentLength = strlen($content);
            if ($contentLength > 2000) {
                $score += 0.3;
                $qualityFactors[] = 'Substantial content length';
            } elseif ($contentLength > 1000) {
                $score += 0.2;
                $qualityFactors[] = 'Moderate content length';
            }

            // Check for legal language
            $legalKeywords = ['liability', 'warranty', 'disclaimer', 'indemnify', 'governing law'];
            $legalCount = 0;
            foreach ($legalKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $legalCount++;
                }
            }
            
            if ($legalCount >= 3) {
                $score += 0.3;
                $qualityFactors[] = 'Contains legal language';
            }

            // Check for update date
            if (preg_match('/\b(updated|last modified|revised)\b.*\b(20\d{2})\b/i', $content)) {
                $score += 0.2;
                $qualityFactors[] = 'Contains update information';
            }

            // Check for contact information
            if (preg_match('/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/', $content)) {
                $score += 0.2;
                $qualityFactors[] = 'Contains contact information';
            }

            return [
                'score' => min($score, 1.0),
                'quality_factors' => $qualityFactors
            ];

        } catch (Exception $e) {
            return [
                'score' => 0.0,
                'quality_factors' => ['Error: ' . $e->getMessage()]
            ];
        }
    }

    private function checkLegalContentQuality(string $url): array
    {
        try {
            $content = $this->fetchUrlContent($url);
            $score = 0.0;
            $qualityFactors = [];

            // Check content length
            $contentLength = strlen($content);
            if ($contentLength > 1000) {
                $score += 0.3;
                $qualityFactors[] = 'Substantial content length';
            } elseif ($contentLength > 500) {
                $score += 0.2;
                $qualityFactors[] = 'Moderate content length';
            }

            // Check for legal language
            $legalKeywords = ['copyright', 'trademark', 'registered', 'all rights reserved', 'disclaimer'];
            $legalCount = 0;
            foreach ($legalKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $legalCount++;
                }
            }
            
            if ($legalCount >= 2) {
                $score += 0.3;
                $qualityFactors[] = 'Contains legal language';
            }

            // Check for company information
            $companyKeywords = ['company', 'corporation', 'llc', 'inc', 'ltd', 'limited'];
            foreach ($companyKeywords as $keyword) {
                if (str_contains(strtolower($content), $keyword)) {
                    $score += 0.2;
                    $qualityFactors[] = 'Contains company information';
                    break;
                }
            }

            // Check for contact information
            if (preg_match('/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/', $content)) {
                $score += 0.2;
                $qualityFactors[] = 'Contains contact information';
            }

            return [
                'score' => min($score, 1.0),
                'quality_factors' => $qualityFactors
            ];

        } catch (Exception $e) {
            return [
                'score' => 0.0,
                'quality_factors' => ['Error: ' . $e->getMessage()]
            ];
        }
    }

    private function getBaseUrl(string $url): string
    {
        $parsed = parse_url($url);
        $scheme = $parsed['scheme'] ?? 'https';
        $host = $parsed['host'] ?? '';
        $port = isset($parsed['port']) ? ':' . $parsed['port'] : '';
        
        return $scheme . '://' . $host . $port;
    }

    private function resolveUrl(string $href, string $baseUrl): ?string
    {
        if (str_starts_with($href, 'http://') || str_starts_with($href, 'https://')) {
            return $href;
        }
        
        if (str_starts_with($href, '//')) {
            return 'https:' . $href;
        }
        
        if (str_starts_with($href, '/')) {
            return $baseUrl . $href;
        }
        
        return $baseUrl . '/' . $href;
    }

    private function isUrlAccessible(string $url): bool
    {
        try {
            $context = stream_context_create([
                'http' => [
                    'timeout' => 5,
                    'user_agent' => 'AiHint-PHP-Scoring/1.0'
                ]
            ]);

            $headers = get_headers($url, 1, $context);
            if (!$headers) {
                return false;
            }

            $statusLine = $headers[0];
            return str_contains($statusLine, '200');
        } catch (Exception $e) {
            return false;
        }
    }

    private function fetchUrlContent(string $url): string
    {
        $context = stream_context_create([
            'http' => [
                'timeout' => $this->timeout,
                'user_agent' => 'AiHint-PHP-Scoring/1.0'
            ]
        ]);

        $content = @file_get_contents($url, false, $context);
        return $content ?: '';
    }
}
