<?php
namespace AIHint\Scoring\Scorers;

use AIHint\Scoring\Metrics\MetricStatus;
use Exception;

class SSLTLSValidator extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->validateSslTls($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function validateSslTls(string $url): array
    {
        if (!$this->isHttps($url)) {
            return [
                'score' => 0.0,
                'details' => [
                    'error' => 'URL is not HTTPS',
                    'checks' => []
                ]
            ];
        }

        $domain = $this->getDomain($url);
        $checks = [];
        $totalScore = 0.0;
        $maxScore = 0.0;

        // Check certificate validity
        $certCheck = $this->checkCertificate($domain);
        $checks[] = $certCheck;
        $totalScore += $certCheck['score'];
        $maxScore += 1.0;

        // Check cipher strength
        $cipherCheck = $this->checkCipherStrength($domain);
        $checks[] = $cipherCheck;
        $totalScore += $cipherCheck['score'];
        $maxScore += 1.0;

        // Check HSTS
        $hstsCheck = $this->checkHSTS($url);
        $checks[] = $hstsCheck;
        $totalScore += $hstsCheck['score'];
        $maxScore += 1.0;

        // Check certificate chain
        $chainCheck = $this->checkCertificateChain($domain);
        $checks[] = $chainCheck;
        $totalScore += $chainCheck['score'];
        $maxScore += 1.0;

        $finalScore = $maxScore > 0 ? $totalScore / $maxScore : 0.0;

        return [
            'score' => $finalScore,
            'details' => [
                'checks' => $checks,
                'total_checks' => count($checks),
                'passed_checks' => count(array_filter($checks, fn($c) => $c['passed']))
            ]
        ];
    }

    private function checkCertificate(string $domain): array
    {
        try {
            $context = stream_context_create([
                'ssl' => [
                    'verify_peer' => true,
                    'verify_peer_name' => true,
                    'capture_peer_cert' => true
                ]
            ]);

            $socket = stream_socket_client(
                "ssl://$domain:443",
                $errno,
                $errstr,
                10,
                STREAM_CLIENT_CONNECT,
                $context
            );

            if (!$socket) {
                return [
                    'name' => 'Certificate Validity',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => "Failed to connect: $errstr"
                ];
            }

            $cert = stream_context_get_params($socket)['options']['ssl']['peer_certificate'];
            $certInfo = openssl_x509_parse($cert);

            fclose($socket);

            $now = time();
            $validFrom = $certInfo['validFrom_time_t'];
            $validTo = $certInfo['validTo_time_t'];

            if ($now < $validFrom) {
                return [
                    'name' => 'Certificate Validity',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'Certificate not yet valid'
                ];
            }

            if ($now > $validTo) {
                return [
                    'name' => 'Certificate Validity',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'Certificate expired'
                ];
            }

            // Check if certificate expires within 30 days
            $daysUntilExpiry = ($validTo - $now) / (24 * 3600);
            if ($daysUntilExpiry < 30) {
                return [
                    'name' => 'Certificate Validity',
                    'passed' => true,
                    'score' => 0.7,
                    'message' => "Certificate expires in {$daysUntilExpiry} days"
                ];
            }

            return [
                'name' => 'Certificate Validity',
                'passed' => true,
                'score' => 1.0,
                'message' => 'Certificate is valid'
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Certificate Validity',
                'passed' => false,
                'score' => 0.0,
                'message' => "Certificate check failed: " . $e->getMessage()
            ];
        }
    }

    private function checkCipherStrength(string $domain): array
    {
        // This is a simplified check - in a real implementation,
        // you'd use a more sophisticated SSL/TLS analysis library
        try {
            $context = stream_context_create([
                'ssl' => [
                    'ciphers' => 'HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA'
                ]
            ]);

            $socket = stream_socket_client(
                "ssl://$domain:443",
                $errno,
                $errstr,
                10,
                STREAM_CLIENT_CONNECT,
                $context
            );

            if ($socket) {
                fclose($socket);
                return [
                    'name' => 'Cipher Strength',
                    'passed' => true,
                    'score' => 1.0,
                    'message' => 'Strong cipher suite detected'
                ];
            }

            return [
                'name' => 'Cipher Strength',
                'passed' => false,
                'score' => 0.0,
                'message' => 'Weak cipher suite or connection failed'
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Cipher Strength',
                'passed' => false,
                'score' => 0.0,
                'message' => "Cipher check failed: " . $e->getMessage()
            ];
        }
    }

    private function checkHSTS(string $url): array
    {
        try {
            $headers = get_headers($url, 1);
            
            if (!$headers) {
                return [
                    'name' => 'HSTS Header',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'Failed to fetch headers'
                ];
            }

            $hstsHeader = $headers['Strict-Transport-Security'] ?? null;
            
            if (!$hstsHeader) {
                return [
                    'name' => 'HSTS Header',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'HSTS header not present'
                ];
            }

            // Check if HSTS includes includeSubDomains and max-age
            $hasIncludeSubDomains = strpos($hstsHeader, 'includeSubDomains') !== false;
            $hasMaxAge = preg_match('/max-age=(\d+)/', $hstsHeader, $matches);
            
            if ($hasMaxAge) {
                $maxAge = (int)$matches[1];
                if ($maxAge >= 31536000) { // 1 year
                    $score = $hasIncludeSubDomains ? 1.0 : 0.8;
                    return [
                        'name' => 'HSTS Header',
                        'passed' => true,
                        'score' => $score,
                        'message' => 'HSTS properly configured' . ($hasIncludeSubDomains ? ' with includeSubDomains' : '')
                    ];
                }
            }

            return [
                'name' => 'HSTS Header',
                'passed' => true,
                'score' => 0.5,
                'message' => 'HSTS present but not optimally configured'
            ];

        } catch (Exception $e) {
            return [
                'name' => 'HSTS Header',
                'passed' => false,
                'score' => 0.0,
                'message' => "HSTS check failed: " . $e->getMessage()
            ];
        }
    }

    private function checkCertificateChain(string $domain): array
    {
        try {
            $context = stream_context_create([
                'ssl' => [
                    'verify_peer' => true,
                    'verify_peer_name' => true,
                    'capture_peer_cert_chain' => true
                ]
            ]);

            $socket = stream_socket_client(
                "ssl://$domain:443",
                $errno,
                $errstr,
                10,
                STREAM_CLIENT_CONNECT,
                $context
            );

            if (!$socket) {
                return [
                    'name' => 'Certificate Chain',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => "Failed to connect: $errstr"
                ];
            }

            $params = stream_context_get_params($socket);
            $chain = $params['options']['ssl']['peer_certificate_chain'] ?? [];

            fclose($socket);

            if (count($chain) < 2) {
                return [
                    'name' => 'Certificate Chain',
                    'passed' => false,
                    'score' => 0.0,
                    'message' => 'Incomplete certificate chain'
                ];
            }

            return [
                'name' => 'Certificate Chain',
                'passed' => true,
                'score' => 1.0,
                'message' => 'Complete certificate chain present'
            ];

        } catch (Exception $e) {
            return [
                'name' => 'Certificate Chain',
                'passed' => false,
                'score' => 0.0,
                'message' => "Certificate chain check failed: " . $e->getMessage()
            ];
        }
    }
}
