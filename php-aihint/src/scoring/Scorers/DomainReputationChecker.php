<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class DomainReputationChecker extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->checkDomainReputation($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function checkDomainReputation(string $url): array
    {
        $domain = $this->getDomain($url);
        $checks = [];
        $totalScore = 0.0;
        $maxScore = 0.0;

        // WHOIS data analysis
        $whoisCheck = $this->checkWhoisData($domain);
        $checks[] = $whoisCheck;
        $totalScore += $whoisCheck['score'];
        $maxScore += 1.0;

        // Blacklist checking
        $blacklistCheck = $this->checkBlacklists($domain);
        $checks[] = $blacklistCheck;
        $totalScore += $blacklistCheck['score'];
        $maxScore += 1.0;

        // DNS reputation
        $dnsCheck = $this->checkDnsReputation($domain);
        $checks[] = $dnsCheck;
        $totalScore += $dnsCheck['score'];
        $maxScore += 1.0;

        // Registrar reputation
        $registrarCheck = $this->checkRegistrarReputation($domain);
        $checks[] = $registrarCheck;
        $totalScore += $registrarCheck['score'];
        $maxScore += 1.0;

        $finalScore = $maxScore > 0 ? $totalScore / $maxScore : 0.0;

        return [
            'score' => $finalScore,
            'details' => [
                'domain' => $domain,
                'checks' => $checks,
                'total_checks' => count($checks),
                'passed_checks' => count(array_filter($checks, fn($c) => $c['passed']))
            ]
        ];
    }

    private function checkWhoisData(string $domain): array
    {
        try {
            // Use a simple WHOIS lookup (this is a basic implementation)
            $whoisData = $this->getWhoisData($domain);
            
            if (empty($whoisData)) {
                return [
                    'name' => 'WHOIS Data',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'No WHOIS data available'
                ];
            }

            $score = 0.0;
            $issues = [];

            // Check registration date
            if (isset($whoisData['creation_date'])) {
                $creationDate = strtotime($whoisData['creation_date']);
                $daysOld = (time() - $creationDate) / (24 * 3600);
                
                if ($daysOld < 30) {
                    $issues[] = 'Domain registered less than 30 days ago';
                    $score += 0.3;
                } elseif ($daysOld < 365) {
                    $score += 0.6;
                } else {
                    $score += 1.0;
                }
            }

            // Check registrar
            if (isset($whoisData['registrar'])) {
                $registrar = strtolower($whoisData['registrar']);
                $suspiciousRegistrars = ['namecheap', 'godaddy', '1and1', 'enom'];
                
                if (in_array($registrar, $suspiciousRegistrars)) {
                    $score += 0.8; // Good registrars
                } else {
                    $score += 0.5; // Unknown registrar
                }
            }

            // Check contact information
            if (isset($whoisData['registrant_organization']) && !empty($whoisData['registrant_organization'])) {
                $score += 0.2;
            }

            if (isset($whoisData['registrant_country']) && !empty($whoisData['registrant_country'])) {
                $score += 0.1;
            }

            return [
                'name' => 'WHOIS Data',
                'passed' => $score > 0.5,
                'score' => min($score, 1.0),
                'message' => empty($issues) ? 'WHOIS data looks legitimate' : implode(', ', $issues),
                'details' => $whoisData
            ];

        } catch (Exception $e) {
            return [
                'name' => 'WHOIS Data',
                'passed' => false,
                'score' => 0.0,
                'message' => 'WHOIS check failed: ' . $e->getMessage()
            ];
        }
    }

    private function checkBlacklists(string $domain): array
    {
        $blacklists = [
            'Spamhaus' => 'https://check.spamhaus.org/listings/dbl.txt',
            'Surbl' => 'https://www.surbl.org/surbl-analysis',
            'PhishTank' => 'https://checkurl.phishtank.com/checkurl/'
        ];

        $blacklisted = [];
        $totalChecks = 0;

        foreach ($blacklists as $name => $url) {
            $totalChecks++;
            try {
                if ($this->isDomainBlacklisted($domain, $url)) {
                    $blacklisted[] = $name;
                }
            } catch (Exception $e) {
                // Skip failed checks
            }
        }

        $score = empty($blacklisted) ? 1.0 : 0.0;

        return [
            'name' => 'Blacklist Check',
            'passed' => empty($blacklisted),
            'score' => $score,
            'message' => empty($blacklisted) ? 'Not blacklisted' : 'Blacklisted on: ' . implode(', ', $blacklisted),
            'details' => [
                'blacklisted_on' => $blacklisted,
                'total_checks' => $totalChecks
            ]
        ];
    }

    private function checkDnsReputation(string $domain): array
    {
        try {
            $score = 0.0;
            $issues = [];

            // Check if domain resolves
            $ip = gethostbyname($domain);
            if ($ip === $domain) {
                return [
                    'name' => 'DNS Reputation',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'Domain does not resolve'
                ];
            }

            $score += 0.3; // Domain resolves

            // Check for suspicious IP ranges
            if ($this->isSuspiciousIP($ip)) {
                $issues[] = 'Suspicious IP range';
                $score += 0.2;
            } else {
                $score += 0.4;
            }

            // Check for multiple A records (potential load balancing)
            $records = dns_get_record($domain, DNS_A);
            if (count($records) > 1) {
                $score += 0.2; // Multiple A records suggest legitimate service
            }

            // Check for MX records (email capability)
            $mxRecords = dns_get_record($domain, DNS_MX);
            if (!empty($mxRecords)) {
                $score += 0.1; // Has email capability
            }

            return [
                'name' => 'DNS Reputation',
                'passed' => $score > 0.5,
                'score' => min($score, 1.0),
                'message' => empty($issues) ? 'DNS configuration looks legitimate' : implode(', ', $issues),
                'details' => [
                    'ip' => $ip,
                    'a_records' => count($records),
                    'mx_records' => count($mxRecords)
                ]
            ];

        } catch (Exception $e) {
            return [
                'name' => 'DNS Reputation',
                'passed' => false,
                'score' => 0.0,
                'message' => 'DNS check failed: ' . $e->getMessage()
            ];
        }
    }

    private function checkRegistrarReputation(string $domain): array
    {
        try {
            $whoisData = $this->getWhoisData($domain);
            $registrar = $whoisData['registrar'] ?? 'Unknown';

            // Known good registrars
            $goodRegistrars = [
                'GoDaddy', 'Namecheap', 'Google Domains', 'Cloudflare',
                'Network Solutions', 'Register.com', '1&1 IONOS'
            ];

            // Known suspicious registrars
            $suspiciousRegistrars = [
                'Freenom', 'Name.com', 'Dynadot'
            ];

            $registrarLower = strtolower($registrar);
            $score = 0.5; // Default score for unknown registrars

            foreach ($goodRegistrars as $good) {
                if (str_contains($registrarLower, strtolower($good))) {
                    $score = 1.0;
                    break;
                }
            }

            foreach ($suspiciousRegistrars as $suspicious) {
                if (str_contains($registrarLower, strtolower($suspicious))) {
                    $score = 0.3;
                    break;
                }
            }

            return [
                'name' => 'Registrar Reputation',
                'passed' => $score > 0.6,
                'score' => $score,
                'message' => "Registrar: $registrar",
                'details' => ['registrar' => $registrar]
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Registrar Reputation',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Registrar check failed: ' . $e->getMessage()
            ];
        }
    }

    private function getWhoisData(string $domain): array
    {
        // This is a simplified WHOIS implementation
        // In a real implementation, you'd use a proper WHOIS library
        try {
            $whoisServer = 'whois.verisign-grs.com';
            $fp = fsockopen($whoisServer, 43, $errno, $errstr, 10);
            
            if (!$fp) {
                return [];
            }

            fwrite($fp, $domain . "\r\n");
            $response = '';
            
            while (!feof($fp)) {
                $response .= fgets($fp, 128);
            }
            
            fclose($fp);

            // Parse basic WHOIS data
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
                    
                    switch ($key) {
                        case 'creation date':
                        case 'created on':
                        case 'domain_dateregistered':
                            $data['creation_date'] = $value;
                            break;
                        case 'registrar':
                        case 'sponsoring registrar':
                            $data['registrar'] = $value;
                            break;
                        case 'registrant organization':
                        case 'org':
                            $data['registrant_organization'] = $value;
                            break;
                        case 'registrant country':
                        case 'country':
                            $data['registrant_country'] = $value;
                            break;
                    }
                }
            }

            return $data;

        } catch (Exception $e) {
            return [];
        }
    }

    private function isDomainBlacklisted(string $domain, string $blacklistUrl): bool
    {
        // This is a simplified implementation
        // In a real implementation, you'd properly check against blacklist APIs
        try {
            $context = stream_context_create([
                'http' => [
                    'timeout' => 5,
                    'user_agent' => 'AiHint-PHP-Scoring/1.0'
                ]
            ]);

            $content = @file_get_contents($blacklistUrl, false, $context);
            return $content !== false && str_contains($content, $domain);

        } catch (Exception $e) {
            return false;
        }
    }

    private function isSuspiciousIP(string $ip): bool
    {
        // Check for suspicious IP ranges
        $suspiciousRanges = [
            '10.0.0.0/8',     // Private networks
            '172.16.0.0/12',  // Private networks
            '192.168.0.0/16', // Private networks
            '127.0.0.0/8'     // Loopback
        ];

        foreach ($suspiciousRanges as $range) {
            if ($this->ipInRange($ip, $range)) {
                return true;
            }
        }

        return false;
    }

    private function ipInRange(string $ip, string $range): bool
    {
        if (str_contains($range, '/')) {
            [$subnet, $bits] = explode('/', $range);
            $ipLong = ip2long($ip);
            $subnetLong = ip2long($subnet);
            $mask = -1 << (32 - (int)$bits);
            return ($ipLong & $mask) === ($subnetLong & $mask);
        }
        
        return $ip === $range;
    }
}
