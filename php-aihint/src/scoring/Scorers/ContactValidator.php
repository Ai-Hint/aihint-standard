<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class ContactValidator extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->validateContact($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function validateContact(string $url): array
    {
        try {
            $checks = [];
            $totalScore = 0.0;
            $maxScore = 0.0;

            // Check for contact page
            $contactPageCheck = $this->checkContactPage($url);
            $checks[] = $contactPageCheck;
            $totalScore += $contactPageCheck['score'];
            $maxScore += 1.0;

            // Check for email addresses
            $emailCheck = $this->checkEmailAddresses($url);
            $checks[] = $emailCheck;
            $totalScore += $emailCheck['score'];
            $maxScore += 1.0;

            // Check for phone numbers
            $phoneCheck = $this->checkPhoneNumbers($url);
            $checks[] = $phoneCheck;
            $totalScore += $phoneCheck['score'];
            $maxScore += 1.0;

            // Check for physical address
            $addressCheck = $this->checkPhysicalAddress($url);
            $checks[] = $addressCheck;
            $totalScore += $addressCheck['score'];
            $maxScore += 1.0;

            // Check for social media presence
            $socialCheck = $this->checkSocialMedia($url);
            $checks[] = $socialCheck;
            $totalScore += $socialCheck['score'];
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

    private function checkContactPage(string $url): array
    {
        try {
            $contactUrls = $this->findContactUrls($url);
            
            if (empty($contactUrls)) {
                return [
                    'name' => 'Contact Page',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No contact page found',
                    'urls_checked' => []
                ];
            }

            // Check if any contact page is accessible
            $accessibleUrls = [];
            foreach ($contactUrls as $contactUrl) {
                if ($this->isUrlAccessible($contactUrl)) {
                    $accessibleUrls[] = $contactUrl;
                }
            }

            if (empty($accessibleUrls)) {
                return [
                    'name' => 'Contact Page',
                    'passed' => false,
                    'score' => 0.3,
                    'message' => 'Contact page found but not accessible',
                    'urls_checked' => $contactUrls
                ];
            }

            return [
                'name' => 'Contact Page',
                'passed' => true,
                'score' => 1.0,
                'message' => 'Contact page found and accessible',
                'urls_checked' => $contactUrls,
                'accessible_urls' => $accessibleUrls
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Contact Page',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Contact page check failed: ' . $e->getMessage(),
                'urls_checked' => []
            ];
        }
    }

    private function checkEmailAddresses(string $url): array
    {
        try {
            $emails = $this->findEmailAddresses($url);
            
            if (empty($emails)) {
                return [
                    'name' => 'Email Addresses',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No email addresses found',
                    'emails' => []
                ];
            }

            $validEmails = [];
            $invalidEmails = [];

            foreach ($emails as $email) {
                if ($this->isValidEmail($email)) {
                    $validEmails[] = $email;
                } else {
                    $invalidEmails[] = $email;
                }
            }

            $score = count($validEmails) > 0 ? 1.0 : 0.0;

            return [
                'name' => 'Email Addresses',
                'passed' => count($validEmails) > 0,
                'score' => $score,
                'message' => count($validEmails) . ' valid email(s) found',
                'emails' => $emails,
                'valid_emails' => $validEmails,
                'invalid_emails' => $invalidEmails
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Email Addresses',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Email check failed: ' . $e->getMessage(),
                'emails' => []
            ];
        }
    }

    private function checkPhoneNumbers(string $url): array
    {
        try {
            $phones = $this->findPhoneNumbers($url);
            
            if (empty($phones)) {
                return [
                    'name' => 'Phone Numbers',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No phone numbers found',
                    'phones' => []
                ];
            }

            $validPhones = [];
            $invalidPhones = [];

            foreach ($phones as $phone) {
                if ($this->isValidPhone($phone)) {
                    $validPhones[] = $phone;
                } else {
                    $invalidPhones[] = $phone;
                }
            }

            $score = count($validPhones) > 0 ? 1.0 : 0.0;

            return [
                'name' => 'Phone Numbers',
                'passed' => count($validPhones) > 0,
                'score' => $score,
                'message' => count($validPhones) . ' valid phone number(s) found',
                'phones' => $phones,
                'valid_phones' => $validPhones,
                'invalid_phones' => $invalidPhones
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Phone Numbers',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Phone check failed: ' . $e->getMessage(),
                'phones' => []
            ];
        }
    }

    private function checkPhysicalAddress(string $url): array
    {
        try {
            $addresses = $this->findPhysicalAddresses($url);
            
            if (empty($addresses)) {
                return [
                    'name' => 'Physical Address',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No physical address found',
                    'addresses' => []
                ];
            }

            $validAddresses = [];
            $invalidAddresses = [];

            foreach ($addresses as $address) {
                if ($this->isValidAddress($address)) {
                    $validAddresses[] = $address;
                } else {
                    $invalidAddresses[] = $address;
                }
            }

            $score = count($validAddresses) > 0 ? 1.0 : 0.0;

            return [
                'name' => 'Physical Address',
                'passed' => count($validAddresses) > 0,
                'score' => $score,
                'message' => count($validAddresses) . ' valid address(es) found',
                'addresses' => $addresses,
                'valid_addresses' => $validAddresses,
                'invalid_addresses' => $invalidAddresses
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Physical Address',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Address check failed: ' . $e->getMessage(),
                'addresses' => []
            ];
        }
    }

    private function checkSocialMedia(string $url): array
    {
        try {
            $socialLinks = $this->findSocialMediaLinks($url);
            
            if (empty($socialLinks)) {
                return [
                    'name' => 'Social Media',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No social media links found',
                    'social_links' => []
                ];
            }

            $validLinks = [];
            $invalidLinks = [];

            foreach ($socialLinks as $platform => $links) {
                foreach ($links as $link) {
                    if ($this->isValidSocialLink($platform, $link)) {
                        $validLinks[$platform][] = $link;
                    } else {
                        $invalidLinks[$platform][] = $link;
                    }
                }
            }

            $score = count($validLinks) > 0 ? min(count($validLinks) * 0.2, 1.0) : 0.0;

            return [
                'name' => 'Social Media',
                'passed' => count($validLinks) > 0,
                'score' => $score,
                'message' => count($validLinks) . ' social media platform(s) found',
                'social_links' => $socialLinks,
                'valid_links' => $validLinks,
                'invalid_links' => $invalidLinks
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Social Media',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Social media check failed: ' . $e->getMessage(),
                'social_links' => []
            ];
        }
    }

    private function findContactUrls(string $url): array
    {
        $contactUrls = [];
        $baseUrl = $this->getBaseUrl($url);
        
        // Common contact page URL patterns
        $contactPaths = [
            '/contact',
            '/contact-us',
            '/contact_us',
            '/contact.html',
            '/contact.php',
            '/about/contact',
            '/support/contact',
            '/help/contact'
        ];

        foreach ($contactPaths as $path) {
            $contactUrls[] = $baseUrl . $path;
        }

        // Try to find contact links on the main page
        try {
            $content = $this->fetchUrlContent($url);
            $contactLinks = $this->extractContactLinks($content, $baseUrl);
            $contactUrls = array_merge($contactUrls, $contactLinks);
        } catch (Exception $e) {
            // Ignore errors when fetching main page
        }

        return array_unique($contactUrls);
    }

    private function extractContactLinks(string $content, string $baseUrl): array
    {
        $links = [];
        
        // Look for links containing contact-related keywords
        $contactKeywords = ['contact', 'about', 'support', 'help', 'reach'];
        
        preg_match_all('/<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<\/a>/i', $content, $matches);
        
        foreach ($matches[1] as $href) {
            $hrefLower = strtolower($href);
            foreach ($contactKeywords as $keyword) {
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

    private function findEmailAddresses(string $url): array
    {
        $emails = [];
        $urls = [$url];
        
        // Also check contact pages
        $contactUrls = $this->findContactUrls($url);
        $urls = array_merge($urls, $contactUrls);

        foreach ($urls as $checkUrl) {
            try {
                $content = $this->fetchUrlContent($checkUrl);
                preg_match_all('/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/', $content, $matches);
                $emails = array_merge($emails, $matches[0]);
            } catch (Exception $e) {
                // Ignore errors
            }
        }

        return array_unique($emails);
    }

    private function findPhoneNumbers(string $url): array
    {
        $phones = [];
        $urls = [$url];
        
        // Also check contact pages
        $contactUrls = $this->findContactUrls($url);
        $urls = array_merge($urls, $contactUrls);

        foreach ($urls as $checkUrl) {
            try {
                $content = $this->fetchUrlContent($checkUrl);
                
                // Various phone number patterns
                $patterns = [
                    '/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/',  // US format
                    '/\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b/', // US format with parentheses
                    '/\b\+1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b/', // International US
                    '/\b\+\d{1,3}[-.]?\d{1,4}[-.]?\d{1,4}[-.]?\d{1,9}\b/' // International
                ];
                
                foreach ($patterns as $pattern) {
                    preg_match_all($pattern, $content, $matches);
                    $phones = array_merge($phones, $matches[0]);
                }
            } catch (Exception $e) {
                // Ignore errors
            }
        }

        return array_unique($phones);
    }

    private function findPhysicalAddresses(string $url): array
    {
        $addresses = [];
        $urls = [$url];
        
        // Also check contact pages
        $contactUrls = $this->findContactUrls($url);
        $urls = array_merge($urls, $contactUrls);

        foreach ($urls as $checkUrl) {
            try {
                $content = $this->fetchUrlContent($checkUrl);
                
                // Look for address patterns
                $addressPatterns = [
                    '/\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct|Circle|Cir)\b/i',
                    '/\b[A-Za-z0-9\s,.-]+\d{5}(?:-\d{4})?\b/', // ZIP code pattern
                    '/\b[A-Za-z0-9\s,.-]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b/' // City, State ZIP
                ];
                
                foreach ($addressPatterns as $pattern) {
                    preg_match_all($pattern, $content, $matches);
                    $addresses = array_merge($addresses, $matches[0]);
                }
            } catch (Exception $e) {
                // Ignore errors
            }
        }

        return array_unique($addresses);
    }

    private function findSocialMediaLinks(string $url): array
    {
        $socialLinks = [];
        $urls = [$url];
        
        // Also check contact pages
        $contactUrls = $this->findContactUrls($url);
        $urls = array_merge($urls, $contactUrls);

        $socialPlatforms = [
            'facebook' => ['facebook.com', 'fb.com'],
            'twitter' => ['twitter.com', 'x.com'],
            'linkedin' => ['linkedin.com'],
            'instagram' => ['instagram.com'],
            'youtube' => ['youtube.com', 'youtu.be'],
            'github' => ['github.com'],
            'reddit' => ['reddit.com']
        ];

        foreach ($urls as $checkUrl) {
            try {
                $content = $this->fetchUrlContent($checkUrl);
                preg_match_all('/<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<\/a>/i', $content, $matches);
                
                foreach ($matches[1] as $href) {
                    $hrefLower = strtolower($href);
                    foreach ($socialPlatforms as $platform => $domains) {
                        foreach ($domains as $domain) {
                            if (str_contains($hrefLower, $domain)) {
                                $socialLinks[$platform][] = $href;
                                break 2;
                            }
                        }
                    }
                }
            } catch (Exception $e) {
                // Ignore errors
            }
        }

        return $socialLinks;
    }

    private function isValidEmail(string $email): bool
    {
        return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
    }

    private function isValidPhone(string $phone): bool
    {
        // Remove all non-digit characters
        $digits = preg_replace('/\D/', '', $phone);
        
        // Check if it has 10-15 digits (reasonable phone number length)
        return strlen($digits) >= 10 && strlen($digits) <= 15;
    }

    private function isValidAddress(string $address): bool
    {
        // Basic address validation
        $address = trim($address);
        
        // Must have at least 10 characters
        if (strlen($address) < 10) {
            return false;
        }
        
        // Must contain numbers (street number)
        if (!preg_match('/\d/', $address)) {
            return false;
        }
        
        // Must contain letters (street name)
        if (!preg_match('/[A-Za-z]/', $address)) {
            return false;
        }
        
        return true;
    }

    private function isValidSocialLink(string $platform, string $link): bool
    {
        $linkLower = strtolower($link);
        
        $platformDomains = [
            'facebook' => ['facebook.com', 'fb.com'],
            'twitter' => ['twitter.com', 'x.com'],
            'linkedin' => ['linkedin.com'],
            'instagram' => ['instagram.com'],
            'youtube' => ['youtube.com', 'youtu.be'],
            'github' => ['github.com'],
            'reddit' => ['reddit.com']
        ];
        
        if (!isset($platformDomains[$platform])) {
            return false;
        }
        
        foreach ($platformDomains[$platform] as $domain) {
            if (str_contains($linkLower, $domain)) {
                return true;
            }
        }
        
        return false;
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
