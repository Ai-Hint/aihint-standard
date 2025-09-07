<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class PrivacyPolicyAnalyzer extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->analyzePrivacyPolicy($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function analyzePrivacyPolicy(string $url): array
    {
        try {
            $checks = [];
            $totalScore = 0.0;
            $maxScore = 0.0;

            // Check for privacy policy presence
            $presenceCheck = $this->checkPrivacyPolicyPresence($url);
            $checks[] = $presenceCheck;
            $totalScore += $presenceCheck['score'];
            $maxScore += 1.0;

            if ($presenceCheck['found']) {
                // Check GDPR compliance
                $gdprCheck = $this->checkGDPRCompliance($url);
                $checks[] = $gdprCheck;
                $totalScore += $gdprCheck['score'];
                $maxScore += 1.0;

                // Check CCPA compliance
                $ccpaCheck = $this->checkCCPACompliance($url);
                $checks[] = $ccpaCheck;
                $totalScore += $ccpaCheck['score'];
                $maxScore += 1.0;

                // Check content quality
                $qualityCheck = $this->checkContentQuality($url);
                $checks[] = $qualityCheck;
                $totalScore += $qualityCheck['score'];
                $maxScore += 1.0;
            }

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

    private function checkPrivacyPolicyPresence(string $url): array
    {
        try {
            $privacyUrls = $this->findPrivacyPolicyUrls($url);
            
            if (empty($privacyUrls)) {
                return [
                    'name' => 'Privacy Policy Presence',
                    'found' => false,
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No privacy policy found',
                    'urls_checked' => []
                ];
            }

            // Check if any of the found URLs are accessible
            $accessibleUrls = [];
            foreach ($privacyUrls as $privacyUrl) {
                if ($this->isUrlAccessible($privacyUrl)) {
                    $accessibleUrls[] = $privacyUrl;
                }
            }

            if (empty($accessibleUrls)) {
                return [
                    'name' => 'Privacy Policy Presence',
                    'found' => true,
                    'passed' => false,
                    'score' => 0.3,
                    'message' => 'Privacy policy found but not accessible',
                    'urls_checked' => $privacyUrls
                ];
            }

            return [
                'name' => 'Privacy Policy Presence',
                'found' => true,
                'passed' => true,
                'score' => 1.0,
                'message' => 'Privacy policy found and accessible',
                'urls_checked' => $privacyUrls,
                'accessible_urls' => $accessibleUrls
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Privacy Policy Presence',
                'found' => false,
                'passed' => false,
                'score' => 0.0,
                'message' => 'Privacy policy check failed: ' . $e->getMessage(),
                'urls_checked' => []
            ];
        }
    }

    private function checkGDPRCompliance(string $url): array
    {
        try {
            $privacyUrls = $this->findPrivacyPolicyUrls($url);
            $gdprKeywords = [
                'gdpr', 'general data protection regulation', 'data protection',
                'personal data', 'data subject', 'consent', 'right to be forgotten',
                'data portability', 'privacy by design', 'data controller',
                'data processor', 'lawful basis', 'legitimate interest'
            ];

            $score = 0.0;
            $foundKeywords = [];
            $totalContent = '';

            foreach ($privacyUrls as $privacyUrl) {
                if ($this->isUrlAccessible($privacyUrl)) {
                    $content = $this->fetchUrlContent($privacyUrl);
                    $totalContent .= ' ' . $content;
                }
            }

            $contentLower = strtolower($totalContent);
            
            foreach ($gdprKeywords as $keyword) {
                if (str_contains($contentLower, $keyword)) {
                    $foundKeywords[] = $keyword;
                    $score += 0.1;
                }
            }

            $score = min($score, 1.0);

            return [
                'name' => 'GDPR Compliance',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => "Found " . count($foundKeywords) . " GDPR-related keywords",
                'found_keywords' => $foundKeywords
            ];

        } catch (Exception $e) {
            return [
                'name' => 'GDPR Compliance',
                'passed' => false,
                'score' => 0.0,
                'message' => 'GDPR check failed: ' . $e->getMessage(),
                'found_keywords' => []
            ];
        }
    }

    private function checkCCPACompliance(string $url): array
    {
        try {
            $privacyUrls = $this->findPrivacyPolicyUrls($url);
            $ccpaKeywords = [
                'ccpa', 'california consumer privacy act', 'california privacy',
                'consumer rights', 'opt-out', 'do not sell', 'personal information',
                'business purpose', 'commercial purpose', 'third party',
                'data broker', 'verifiable consumer request'
            ];

            $score = 0.0;
            $foundKeywords = [];
            $totalContent = '';

            foreach ($privacyUrls as $privacyUrl) {
                if ($this->isUrlAccessible($privacyUrl)) {
                    $content = $this->fetchUrlContent($privacyUrl);
                    $totalContent .= ' ' . $content;
                }
            }

            $contentLower = strtolower($totalContent);
            
            foreach ($ccpaKeywords as $keyword) {
                if (str_contains($contentLower, $keyword)) {
                    $foundKeywords[] = $keyword;
                    $score += 0.1;
                }
            }

            $score = min($score, 1.0);

            return [
                'name' => 'CCPA Compliance',
                'passed' => $score > 0.3,
                'score' => $score,
                'message' => "Found " . count($foundKeywords) . " CCPA-related keywords",
                'found_keywords' => $foundKeywords
            ];

        } catch (Exception $e) {
            return [
                'name' => 'CCPA Compliance',
                'passed' => false,
                'score' => 0.0,
                'message' => 'CCPA check failed: ' . $e->getMessage(),
                'found_keywords' => []
            ];
        }
    }

    private function checkContentQuality(string $url): array
    {
        try {
            $privacyUrls = $this->findPrivacyPolicyUrls($url);
            $score = 0.0;
            $qualityFactors = [];

            foreach ($privacyUrls as $privacyUrl) {
                if ($this->isUrlAccessible($privacyUrl)) {
                    $content = $this->fetchUrlContent($privacyUrl);
                    $contentLength = strlen($content);
                    
                    // Check content length
                    if ($contentLength > 1000) {
                        $score += 0.3;
                        $qualityFactors[] = 'Substantial content length';
                    } elseif ($contentLength > 500) {
                        $score += 0.2;
                        $qualityFactors[] = 'Moderate content length';
                    } else {
                        $qualityFactors[] = 'Short content';
                    }

                    // Check for structured content
                    if (str_contains($content, '<h1>') || str_contains($content, '<h2>')) {
                        $score += 0.2;
                        $qualityFactors[] = 'Structured content with headings';
                    }

                    // Check for contact information
                    if (preg_match('/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/', $content)) {
                        $score += 0.2;
                        $qualityFactors[] = 'Contains contact information';
                    }

                    // Check for update date
                    if (preg_match('/\b(updated|last modified|revised)\b.*\b(20\d{2})\b/i', $content)) {
                        $score += 0.2;
                        $qualityFactors[] = 'Contains update information';
                    }

                    // Check for legal language
                    $legalKeywords = ['terms', 'conditions', 'agreement', 'liability', 'warranty'];
                    $legalCount = 0;
                    foreach ($legalKeywords as $keyword) {
                        if (str_contains(strtolower($content), $keyword)) {
                            $legalCount++;
                        }
                    }
                    
                    if ($legalCount >= 3) {
                        $score += 0.1;
                        $qualityFactors[] = 'Contains legal language';
                    }

                    break; // Only check the first accessible URL
                }
            }

            $score = min($score, 1.0);

            return [
                'name' => 'Content Quality',
                'passed' => $score > 0.5,
                'score' => $score,
                'message' => 'Privacy policy content analysis',
                'quality_factors' => $qualityFactors
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Content Quality',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Content quality check failed: ' . $e->getMessage(),
                'quality_factors' => []
            ];
        }
    }

    private function findPrivacyPolicyUrls(string $url): array
    {
        $privacyUrls = [];
        $baseUrl = $this->getBaseUrl($url);
        
        // Common privacy policy URL patterns
        $privacyPaths = [
            '/privacy',
            '/privacy-policy',
            '/privacy_policy',
            '/privacy.html',
            '/privacy.php',
            '/legal/privacy',
            '/terms/privacy',
            '/policy/privacy',
            '/privacy-policy.html',
            '/privacy-policy.php'
        ];

        foreach ($privacyPaths as $path) {
            $privacyUrls[] = $baseUrl . $path;
        }

        // Try to find privacy policy links on the main page
        try {
            $content = $this->fetchUrlContent($url);
            $privacyLinks = $this->extractPrivacyLinks($content, $baseUrl);
            $privacyUrls = array_merge($privacyUrls, $privacyLinks);
        } catch (Exception $e) {
            // Ignore errors when fetching main page
        }

        return array_unique($privacyUrls);
    }

    private function extractPrivacyLinks(string $content, string $baseUrl): array
    {
        $links = [];
        
        // Look for links containing privacy-related keywords
        $privacyKeywords = ['privacy', 'policy', 'legal', 'terms'];
        
        preg_match_all('/<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<\/a>/i', $content, $matches);
        
        foreach ($matches[1] as $href) {
            $hrefLower = strtolower($href);
            foreach ($privacyKeywords as $keyword) {
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

            $headers = @get_headers($url, 1, $context);
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
