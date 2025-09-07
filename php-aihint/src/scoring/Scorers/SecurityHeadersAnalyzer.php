<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class SecurityHeadersAnalyzer extends BaseScorer
{
    private array $securityHeaders = [
        'Strict-Transport-Security' => 'HSTS',
        'Content-Security-Policy' => 'CSP',
        'X-Frame-Options' => 'X-Frame-Options',
        'X-Content-Type-Options' => 'X-Content-Type-Options',
        'Referrer-Policy' => 'Referrer-Policy',
        'Permissions-Policy' => 'Permissions-Policy',
        'X-XSS-Protection' => 'X-XSS-Protection',
        'Cross-Origin-Embedder-Policy' => 'COEP',
        'Cross-Origin-Opener-Policy' => 'COOP',
        'Cross-Origin-Resource-Policy' => 'CORP'
    ];

    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->analyzeSecurityHeaders($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function analyzeSecurityHeaders(string $url): array
    {
        try {
            $headers = get_headers($url, 1);
            
            if (!$headers) {
                return [
                    'score' => 0.0,
                    'details' => [
                        'error' => 'Failed to fetch headers',
                        'headers_analyzed' => 0,
                        'headers_present' => 0,
                        'header_details' => []
                    ]
                ];
            }

            $headerDetails = [];
            $totalScore = 0.0;
            $headersPresent = 0;

            foreach ($this->securityHeaders as $headerName => $shortName) {
                $headerValue = $headers[$headerName] ?? null;
                $headerCheck = $this->checkHeader($headerName, $headerValue);
                
                $headerDetails[] = $headerCheck;
                $totalScore += $headerCheck['score'];
                
                if ($headerCheck['present']) {
                    $headersPresent++;
                }
            }

            $maxScore = count($this->securityHeaders);
            $finalScore = $maxScore > 0 ? $totalScore / $maxScore : 0.0;

            return [
                'score' => $finalScore,
                'details' => [
                    'headers_analyzed' => count($this->securityHeaders),
                    'headers_present' => $headersPresent,
                    'header_details' => $headerDetails
                ]
            ];

        } catch (Exception $e) {
            return [
                'score' => 0.0,
                'details' => [
                    'error' => $e->getMessage(),
                    'headers_analyzed' => 0,
                    'headers_present' => 0,
                    'header_details' => []
                ]
            ];
        }
    }

    private function checkHeader(string $headerName, ?string $headerValue): array
    {
        if (!$headerValue) {
            return [
                'name' => $headerName,
                'present' => false,
                'score' => 0.0,
                'message' => 'Header not present',
                'value' => null
            ];
        }

        // Normalize header value (handle arrays from get_headers)
        if (is_array($headerValue)) {
            $headerValue = end($headerValue);
        }

        $headerValue = trim($headerValue);

        switch ($headerName) {
            case 'Strict-Transport-Security':
                return $this->checkHSTS($headerValue);
            
            case 'Content-Security-Policy':
                return $this->checkCSP($headerValue);
            
            case 'X-Frame-Options':
                return $this->checkXFrameOptions($headerValue);
            
            case 'X-Content-Type-Options':
                return $this->checkXContentTypeOptions($headerValue);
            
            case 'Referrer-Policy':
                return $this->checkReferrerPolicy($headerValue);
            
            case 'Permissions-Policy':
                return $this->checkPermissionsPolicy($headerValue);
            
            case 'X-XSS-Protection':
                return $this->checkXXSSProtection($headerValue);
            
            case 'Cross-Origin-Embedder-Policy':
                return $this->checkCOEP($headerValue);
            
            case 'Cross-Origin-Opener-Policy':
                return $this->checkCOOP($headerValue);
            
            case 'Cross-Origin-Resource-Policy':
                return $this->checkCORP($headerValue);
            
            default:
                return [
                    'name' => $headerName,
                    'present' => true,
                    'score' => 0.5,
                    'message' => 'Header present but not analyzed',
                    'value' => $headerValue
                ];
        }
    }

    private function checkHSTS(string $value): array
    {
        $hasMaxAge = preg_match('/max-age=(\d+)/', $value, $matches);
        $hasIncludeSubDomains = strpos($value, 'includeSubDomains') !== false;
        $hasPreload = strpos($value, 'preload') !== false;

        if (!$hasMaxAge) {
            return [
                'name' => 'Strict-Transport-Security',
                'present' => true,
                'score' => 0.2,
                'message' => 'HSTS present but missing max-age',
                'value' => $value
            ];
        }

        $maxAge = (int)$matches[1];
        $score = 0.5;

        if ($maxAge >= 31536000) { // 1 year
            $score += 0.3;
        }

        if ($hasIncludeSubDomains) {
            $score += 0.2;
        }

        if ($hasPreload) {
            $score += 0.1;
        }

        return [
            'name' => 'Strict-Transport-Security',
            'present' => true,
            'score' => min($score, 1.0),
            'message' => 'HSTS properly configured',
            'value' => $value
        ];
    }

    private function checkCSP(string $value): array
    {
        $hasDefaultSrc = strpos($value, 'default-src') !== false;
        $hasScriptSrc = strpos($value, 'script-src') !== false;
        $hasStyleSrc = strpos($value, 'style-src') !== false;
        $hasObjectSrc = strpos($value, 'object-src') !== false;
        $hasBaseUri = strpos($value, 'base-uri') !== false;
        $hasFrameAncestors = strpos($value, 'frame-ancestors') !== false;

        $score = 0.2; // Base score for having CSP
        $checks = 0;

        if ($hasDefaultSrc) { $score += 0.2; $checks++; }
        if ($hasScriptSrc) { $score += 0.2; $checks++; }
        if ($hasStyleSrc) { $score += 0.1; $checks++; }
        if ($hasObjectSrc) { $score += 0.1; $checks++; }
        if ($hasBaseUri) { $score += 0.1; $checks++; }
        if ($hasFrameAncestors) { $score += 0.1; $checks++; }

        return [
            'name' => 'Content-Security-Policy',
            'present' => true,
            'score' => min($score, 1.0),
            'message' => "CSP present with $checks directives",
            'value' => $value
        ];
    }

    private function checkXFrameOptions(string $value): array
    {
        $value = strtolower($value);
        
        if ($value === 'deny') {
            return [
                'name' => 'X-Frame-Options',
                'present' => true,
                'score' => 1.0,
                'message' => 'X-Frame-Options set to DENY',
                'value' => $value
            ];
        }
        
        if (strpos($value, 'sameorigin') !== false) {
            return [
                'name' => 'X-Frame-Options',
                'present' => true,
                'score' => 0.7,
                'message' => 'X-Frame-Options set to SAMEORIGIN',
                'value' => $value
            ];
        }
        
        return [
            'name' => 'X-Frame-Options',
            'present' => true,
            'score' => 0.3,
            'message' => 'X-Frame-Options present but not optimal',
            'value' => $value
        ];
    }

    private function checkXContentTypeOptions(string $value): array
    {
        if (strtolower($value) === 'nosniff') {
            return [
                'name' => 'X-Content-Type-Options',
                'present' => true,
                'score' => 1.0,
                'message' => 'X-Content-Type-Options set to nosniff',
                'value' => $value
            ];
        }
        
        return [
            'name' => 'X-Content-Type-Options',
            'present' => true,
            'score' => 0.3,
            'message' => 'X-Content-Type-Options present but not nosniff',
            'value' => $value
        ];
    }

    private function checkReferrerPolicy(string $value): array
    {
        $value = strtolower($value);
        
        $goodPolicies = ['no-referrer', 'same-origin', 'strict-origin', 'strict-origin-when-cross-origin'];
        
        if (in_array($value, $goodPolicies)) {
            return [
                'name' => 'Referrer-Policy',
                'present' => true,
                'score' => 1.0,
                'message' => "Referrer-Policy set to $value",
                'value' => $value
            ];
        }
        
        return [
            'name' => 'Referrer-Policy',
            'present' => true,
            'score' => 0.5,
            'message' => 'Referrer-Policy present but not optimal',
            'value' => $value
        ];
    }

    private function checkPermissionsPolicy(string $value): array
    {
        // Basic check for Permissions-Policy presence
        $directives = explode(',', $value);
        $directiveCount = count(array_filter($directives, fn($d) => !empty(trim($d))));
        
        $score = min(0.2 + ($directiveCount * 0.1), 1.0);
        
        return [
            'name' => 'Permissions-Policy',
            'present' => true,
            'score' => $score,
            'message' => "Permissions-Policy with $directiveCount directives",
            'value' => $value
        ];
    }

    private function checkXXSSProtection(string $value): array
    {
        // X-XSS-Protection is deprecated but still checked
        if (strpos($value, '1') !== false) {
            return [
                'name' => 'X-XSS-Protection',
                'present' => true,
                'score' => 0.5,
                'message' => 'X-XSS-Protection present (deprecated)',
                'value' => $value
            ];
        }
        
        return [
            'name' => 'X-XSS-Protection',
            'present' => true,
            'score' => 0.2,
            'message' => 'X-XSS-Protection present but not enabled',
            'value' => $value
        ];
    }

    private function checkCOEP(string $value): array
    {
        $value = strtolower($value);
        
        if ($value === 'require-corp') {
            return [
                'name' => 'Cross-Origin-Embedder-Policy',
                'present' => true,
                'score' => 1.0,
                'message' => 'COEP set to require-corp',
                'value' => $value
            ];
        }
        
        return [
            'name' => 'Cross-Origin-Embedder-Policy',
            'present' => true,
            'score' => 0.5,
            'message' => 'COEP present but not require-corp',
            'value' => $value
        ];
    }

    private function checkCOOP(string $value): array
    {
        $value = strtolower($value);
        
        if (in_array($value, ['same-origin', 'same-origin-allow-popups'])) {
            return [
                'name' => 'Cross-Origin-Opener-Policy',
                'present' => true,
                'score' => 1.0,
                'message' => "COOP set to $value",
                'value' => $value
            ];
        }
        
        return [
            'name' => 'Cross-Origin-Opener-Policy',
            'present' => true,
            'score' => 0.5,
            'message' => 'COOP present but not optimal',
            'value' => $value
        ];
    }

    private function checkCORP(string $value): array
    {
        $value = strtolower($value);
        
        if (in_array($value, ['same-origin', 'same-site', 'cross-origin'])) {
            return [
                'name' => 'Cross-Origin-Resource-Policy',
                'present' => true,
                'score' => 1.0,
                'message' => "CORP set to $value",
                'value' => $value
            ];
        }
        
        return [
            'name' => 'Cross-Origin-Resource-Policy',
            'present' => true,
            'score' => 0.5,
            'message' => 'CORP present but not optimal',
            'value' => $value
        ];
    }
}
