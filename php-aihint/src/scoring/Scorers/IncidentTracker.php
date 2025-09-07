<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class IncidentTracker extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->trackIncidents($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function trackIncidents(string $url): array
    {
        $domain = $this->getDomain($url);
        $checks = [];
        $totalScore = 0.0;
        $maxScore = 0.0;

        // Security incident history
        $securityCheck = $this->checkSecurityIncidents($domain);
        $checks[] = $securityCheck;
        $totalScore += $securityCheck['score'];
        $maxScore += 1.0;

        // Downtime analysis
        $downtimeCheck = $this->checkDowntimeHistory($domain);
        $checks[] = $downtimeCheck;
        $totalScore += $downtimeCheck['score'];
        $maxScore += 1.0;

        // SSL incident tracking
        $sslCheck = $this->checkSslIncidents($domain);
        $checks[] = $sslCheck;
        $totalScore += $sslCheck['score'];
        $maxScore += 1.0;

        // Reputation incidents
        $reputationCheck = $this->checkReputationIncidents($domain);
        $checks[] = $reputationCheck;
        $totalScore += $reputationCheck['score'];
        $maxScore += 1.0;

        $finalScore = $maxScore > 0 ? $totalScore / $maxScore : 1.0;

        return [
            'score' => $finalScore,
            'details' => [
                'domain' => $domain,
                'checks' => $checks,
                'total_checks' => count($checks),
                'passed_checks' => count(array_filter($checks, fn($c) => $c['passed'])),
                'incidents_found' => $this->countIncidents($checks)
            ]
        ];
    }

    private function checkSecurityIncidents(string $domain): array
    {
        try {
            // This is a simplified implementation
            // In a real implementation, you'd check against security incident databases
            
            $incidents = [];
            $score = 1.0; // Start with perfect score

            // Check for known security issues (simplified)
            $securityKeywords = ['breach', 'hack', 'compromise', 'vulnerability', 'exploit'];
            $domainLower = strtolower($domain);
            
            foreach ($securityKeywords as $keyword) {
                if (str_contains($domainLower, $keyword)) {
                    $incidents[] = "Domain name contains suspicious keyword: $keyword";
                    $score -= 0.3;
                }
            }

            // Check for recent registration (potential for abuse)
            $whoisData = $this->getWhoisData($domain);
            if (isset($whoisData['creation_date'])) {
                $creationDate = strtotime($whoisData['creation_date']);
                $ageInDays = (time() - $creationDate) / (24 * 3600);
                
                if ($ageInDays < 7) {
                    $incidents[] = 'Very recently registered domain (potential for abuse)';
                    $score -= 0.2;
                }
            }

            $score = max($score, 0.0);

            return [
                'name' => 'Security Incidents',
                'passed' => $score > 0.7,
                'score' => $score,
                'message' => empty($incidents) ? 'No security incidents detected' : implode(', ', $incidents),
                'incidents' => $incidents
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Security Incidents',
                'passed' => true,
                'score' => 0.5,
                'message' => 'Security check failed: ' . $e->getMessage(),
                'incidents' => []
            ];
        }
    }

    private function checkDowntimeHistory(string $domain): array
    {
        try {
            // This is a simplified implementation
            // In a real implementation, you'd check against uptime monitoring services
            
            $score = 1.0;
            $issues = [];

            // Check if domain is currently accessible
            $context = stream_context_create([
                'http' => [
                    'timeout' => 5,
                    'user_agent' => 'AiHint-PHP-Scoring/1.0'
                ]
            ]);

            $startTime = microtime(true);
            $response = @file_get_contents("https://$domain", false, $context);
            $responseTime = microtime(true) - $startTime;

            if ($response === false) {
                $issues[] = 'Domain currently inaccessible';
                $score = 0.0;
            } else {
                // Check response time
                if ($responseTime > 5.0) {
                    $issues[] = 'Slow response time';
                    $score -= 0.2;
                } elseif ($responseTime > 2.0) {
                    $score -= 0.1;
                }

                // Check HTTP status
                $httpCode = $this->getHttpResponseCode("https://$domain");
                if ($httpCode >= 400) {
                    $issues[] = "HTTP error: $httpCode";
                    $score -= 0.3;
                }
            }

            $score = max($score, 0.0);

            return [
                'name' => 'Downtime History',
                'passed' => $score > 0.7,
                'score' => $score,
                'message' => empty($issues) ? 'Domain appears stable' : implode(', ', $issues),
                'response_time' => $responseTime ?? null,
                'http_code' => $httpCode ?? null
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Downtime History',
                'passed' => true,
                'score' => 0.5,
                'message' => 'Downtime check failed: ' . $e->getMessage(),
                'response_time' => null,
                'http_code' => null
            ];
        }
    }

    private function checkSslIncidents(string $domain): array
    {
        try {
            $score = 1.0;
            $issues = [];

            // Check SSL certificate status
            $context = stream_context_create([
                'ssl' => [
                    'verify_peer' => true,
                    'verify_peer_name' => true,
                    'capture_peer_cert' => true
                ]
            ]);

            $socket = @stream_socket_client(
                "ssl://$domain:443",
                $errno,
                $errstr,
                5,
                STREAM_CLIENT_CONNECT,
                $context
            );

            if (!$socket) {
                $issues[] = 'SSL connection failed';
                $score = 0.0;
            } else {
                $cert = stream_context_get_params($socket)['options']['ssl']['peer_certificate'];
                $certInfo = openssl_x509_parse($cert);
                
                // Check certificate validity
                $now = time();
                $validFrom = $certInfo['validFrom_time_t'];
                $validTo = $certInfo['validTo_time_t'];

                if ($now < $validFrom || $now > $validTo) {
                    $issues[] = 'SSL certificate invalid';
                    $score = 0.0;
                } else {
                    // Check if certificate expires soon
                    $daysUntilExpiry = ($validTo - $now) / (24 * 3600);
                    if ($daysUntilExpiry < 30) {
                        $issues[] = 'SSL certificate expires soon';
                        $score -= 0.3;
                    }
                }

                fclose($socket);
            }

            $score = max($score, 0.0);

            return [
                'name' => 'SSL Incidents',
                'passed' => $score > 0.7,
                'score' => $score,
                'message' => empty($issues) ? 'SSL appears secure' : implode(', ', $issues),
                'issues' => $issues
            ];

        } catch (Exception $e) {
            return [
                'name' => 'SSL Incidents',
                'passed' => true,
                'score' => 0.5,
                'message' => 'SSL check failed: ' . $e->getMessage(),
                'issues' => []
            ];
        }
    }

    private function checkReputationIncidents(string $domain): array
    {
        try {
            $score = 1.0;
            $incidents = [];

            // Check for suspicious patterns in domain name
            $suspiciousPatterns = [
                '/\d{4,}/' => 'Contains many numbers',
                '/[^a-zA-Z0-9.-]/' => 'Contains suspicious characters',
                '/\b(free|download|crack|hack|virus|malware)\b/i' => 'Contains suspicious keywords'
            ];

            foreach ($suspiciousPatterns as $pattern => $description) {
                if (preg_match($pattern, $domain)) {
                    $incidents[] = $description;
                    $score -= 0.2;
                }
            }

            // Check for typosquatting patterns
            $commonDomains = ['google', 'facebook', 'amazon', 'microsoft', 'apple', 'netflix'];
            foreach ($commonDomains as $common) {
                if (str_contains(strtolower($domain), $common)) {
                    $incidents[] = 'Potential typosquatting of ' . $common;
                    $score -= 0.3;
                }
            }

            $score = max($score, 0.0);

            return [
                'name' => 'Reputation Incidents',
                'passed' => $score > 0.7,
                'score' => $score,
                'message' => empty($incidents) ? 'No reputation issues detected' : implode(', ', $incidents),
                'incidents' => $incidents
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Reputation Incidents',
                'passed' => true,
                'score' => 0.5,
                'message' => 'Reputation check failed: ' . $e->getMessage(),
                'incidents' => []
            ];
        }
    }

    private function countIncidents(array $checks): int
    {
        $count = 0;
        foreach ($checks as $check) {
            if (isset($check['incidents'])) {
                $count += count($check['incidents']);
            }
            if (isset($check['issues'])) {
                $count += count($check['issues']);
            }
        }
        return $count;
    }

    private function getWhoisData(string $domain): array
    {
        try {
            $whoisServer = 'whois.verisign-grs.com';
            $fp = fsockopen($whoisServer, 43, $errno, $errstr, 5);
            
            if (!$fp) {
                return [];
            }

            fwrite($fp, $domain . "\r\n");
            $response = '';
            
            while (!feof($fp)) {
                $response .= fgets($fp, 128);
            }
            
            fclose($fp);

            $data = [];
            $lines = explode("\n", $response);
            
            foreach ($lines as $line) {
                $line = trim($line);
                if (empty($line) || str_starts_with($line, '%') || str_starts_with($line, '#')) {
                    continue;
                }
                
                if (str_contains($line, ':')) {
                    [$key, $value] = explode(':', $line, 2);
                    $key = strtolower(trim($key));
                    $value = trim($value);
                    
                    if (in_array($key, ['creation date', 'created on', 'domain_dateregistered'])) {
                        $data['creation_date'] = $value;
                        break;
                    }
                }
            }

            return $data;

        } catch (Exception $e) {
            return [];
        }
    }

    private function getHttpResponseCode(string $url): int
    {
        $headers = get_headers($url, 1);
        if (!$headers) {
            return 0;
        }
        
        $statusLine = $headers[0];
        preg_match('/HTTP\/\d\.\d\s+(\d+)/', $statusLine, $matches);
        return isset($matches[1]) ? (int)$matches[1] : 0;
    }
}
