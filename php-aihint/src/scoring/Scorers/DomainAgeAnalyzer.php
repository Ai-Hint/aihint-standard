<?php
namespace AIHint\Scoring\Scorers;

use Exception;

class DomainAgeAnalyzer extends BaseScorer
{
    public function score(string $url): array
    {
        [$result, $executionTime] = $this->measureExecutionTime(function() use ($url) {
            return $this->analyzeDomainAge($url);
        });

        return [
            'score' => $result['score'],
            'details' => $result['details'],
            'execution_time_ms' => $executionTime
        ];
    }

    private function analyzeDomainAge(string $url): array
    {
        $domain = $this->getDomain($url);
        
        try {
            $whoisData = $this->getWhoisData($domain);
            
            if (empty($whoisData) || !isset($whoisData['creation_date'])) {
                return [
                    'score' => 0.0,
                    'details' => [
                        'error' => 'Unable to determine domain age',
                        'domain' => $domain,
                        'age_days' => null,
                        'age_category' => 'unknown'
                    ]
                ];
            }

            $creationDate = strtotime($whoisData['creation_date']);
            $currentTime = time();
            $ageInDays = ($currentTime - $creationDate) / (24 * 3600);
            $ageInYears = $ageInDays / 365.25;

            $score = $this->calculateAgeScore($ageInDays);
            $ageCategory = $this->getAgeCategory($ageInDays);

            return [
                'score' => $score,
                'details' => [
                    'domain' => $domain,
                    'creation_date' => $whoisData['creation_date'],
                    'age_days' => round($ageInDays),
                    'age_years' => round($ageInYears, 2),
                    'age_category' => $ageCategory,
                    'score_breakdown' => $this->getScoreBreakdown($ageInDays)
                ]
            ];

        } catch (Exception $e) {
            return [
                'score' => 0.0,
                'details' => [
                    'error' => $e->getMessage(),
                    'domain' => $domain,
                    'age_days' => null,
                    'age_category' => 'unknown'
                ]
            ];
        }
    }

    private function calculateAgeScore(float $ageInDays): float
    {
        // Scoring based on domain age
        if ($ageInDays < 0) {
            return 0.0; // Invalid date
        }
        
        if ($ageInDays < 1) {
            return 0.1; // Very new domain (less than 1 day)
        }
        
        if ($ageInDays < 7) {
            return 0.2; // Very new domain (less than 1 week)
        }
        
        if ($ageInDays < 30) {
            return 0.3; // New domain (less than 1 month)
        }
        
        if ($ageInDays < 90) {
            return 0.5; // Relatively new domain (less than 3 months)
        }
        
        if ($ageInDays < 180) {
            return 0.6; // Somewhat established (less than 6 months)
        }
        
        if ($ageInDays < 365) {
            return 0.7; // Established domain (less than 1 year)
        }
        
        if ($ageInDays < 730) {
            return 0.8; // Well-established domain (1-2 years)
        }
        
        if ($ageInDays < 1825) {
            return 0.9; // Mature domain (2-5 years)
        }
        
        return 1.0; // Very mature domain (5+ years)
    }

    private function getAgeCategory(float $ageInDays): string
    {
        if ($ageInDays < 1) {
            return 'very_new';
        }
        
        if ($ageInDays < 7) {
            return 'new';
        }
        
        if ($ageInDays < 30) {
            return 'recent';
        }
        
        if ($ageInDays < 90) {
            return 'young';
        }
        
        if ($ageInDays < 180) {
            return 'developing';
        }
        
        if ($ageInDays < 365) {
            return 'established';
        }
        
        if ($ageInDays < 730) {
            return 'mature';
        }
        
        if ($ageInDays < 1825) {
            return 'well_established';
        }
        
        return 'very_mature';
    }

    private function getScoreBreakdown(float $ageInDays): array
    {
        $breakdown = [];
        
        // Age factor
        $breakdown['age_factor'] = $this->calculateAgeScore($ageInDays);
        
        // Stability factor (based on age)
        if ($ageInDays < 30) {
            $breakdown['stability_factor'] = 0.2;
        } elseif ($ageInDays < 90) {
            $breakdown['stability_factor'] = 0.4;
        } elseif ($ageInDays < 365) {
            $breakdown['stability_factor'] = 0.6;
        } elseif ($ageInDays < 730) {
            $breakdown['stability_factor'] = 0.8;
        } else {
            $breakdown['stability_factor'] = 1.0;
        }
        
        // Trust factor (older domains are generally more trusted)
        if ($ageInDays < 7) {
            $breakdown['trust_factor'] = 0.1;
        } elseif ($ageInDays < 30) {
            $breakdown['trust_factor'] = 0.3;
        } elseif ($ageInDays < 90) {
            $breakdown['trust_factor'] = 0.5;
        } elseif ($ageInDays < 365) {
            $breakdown['trust_factor'] = 0.7;
        } elseif ($ageInDays < 730) {
            $breakdown['trust_factor'] = 0.9;
        } else {
            $breakdown['trust_factor'] = 1.0;
        }
        
        // Overall score is weighted average
        $breakdown['overall_score'] = (
            $breakdown['age_factor'] * 0.4 +
            $breakdown['stability_factor'] * 0.3 +
            $breakdown['trust_factor'] * 0.3
        );
        
        return $breakdown;
    }

    private function getWhoisData(string $domain): array
    {
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

            // Parse WHOIS data for creation date
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
                    
                    if (in_array($key, ['creation date', 'created on', 'domain_dateregistered', 'registered'])) {
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
}
