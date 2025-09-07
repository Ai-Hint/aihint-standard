<?php
namespace AIHint\Scoring;

use AIHint\Scoring\Metrics\SecurityMetrics;
use AIHint\Scoring\Metrics\ReputationMetrics;
use AIHint\Scoring\Metrics\ComplianceMetrics;
use AIHint\Scoring\Scorers\SSLTLSValidator;
use AIHint\Scoring\Scorers\SecurityHeadersAnalyzer;
use AIHint\Scoring\Scorers\MalwareChecker;
use AIHint\Scoring\Scorers\DomainReputationChecker;
use AIHint\Scoring\Scorers\DomainAgeAnalyzer;
use AIHint\Scoring\Scorers\IncidentTracker;
use AIHint\Scoring\Scorers\PrivacyPolicyAnalyzer;
use AIHint\Scoring\Scorers\ContactValidator;
use AIHint\Scoring\Scorers\ComplianceChecker;
use DateTime;
use Exception;

class TrustScoringEngine
{
    private $config;
    private $securityMetrics;
    private $reputationMetrics;
    private $complianceMetrics;
    private $scorers;
    private $weights;

    public function __construct(array $config = [])
    {
        $this->config = $config;
        
        // Initialize metric collectors
        $this->securityMetrics = new SecurityMetrics();
        $this->reputationMetrics = new ReputationMetrics();
        $this->complianceMetrics = new ComplianceMetrics();
        
        // Initialize scorers
        $this->scorers = [
            'ssl_tls' => new SSLTLSValidator($config['ssl'] ?? []),
            'security_headers' => new SecurityHeadersAnalyzer($config['headers'] ?? []),
            'malware' => new MalwareChecker($config['malware'] ?? []),
            'domain_reputation' => new DomainReputationChecker($config['reputation'] ?? []),
            'domain_age' => new DomainAgeAnalyzer($config['domain_age'] ?? []),
            'incidents' => new IncidentTracker($config['incidents'] ?? []),
            'privacy_policy' => new PrivacyPolicyAnalyzer($config['privacy'] ?? []),
            'contact' => new ContactValidator($config['contact'] ?? []),
            'compliance' => new ComplianceChecker($config['compliance'] ?? [])
        ];
        
        // Scoring weights (can be configured)
        $this->weights = $config['weights'] ?? [
            'security' => 0.4,      // 40% weight for security metrics
            'reputation' => 0.35,   // 35% weight for reputation signals
            'compliance' => 0.25    // 25% weight for compliance metrics
        ];
    }

    public function scoreWebsite(string $url): ScoringResult
    {
        $warnings = [];
        $errors = [];
        $detailedMetrics = [];
        
        try {
            // Run all scoring tasks
            $securityResult = $this->scoreSecurityMetrics($url);
            $reputationResult = $this->scoreReputationMetrics($url);
            $complianceResult = $this->scoreComplianceMetrics($url);
            
            // Collect detailed metrics from each phase
            $detailedMetrics = [
                'security' => $securityResult['metrics'] ?? [],
                'reputation' => $reputationResult['metrics'] ?? [],
                'compliance' => $complianceResult['metrics'] ?? []
            ];
            
            // Calculate weighted final score
            $finalScore = $this->calculateWeightedScore(
                $securityResult['score'],
                $reputationResult['score'],
                $complianceResult['score']
            );
            
            // Calculate confidence based on data completeness
            $confidence = $this->calculateConfidence($detailedMetrics);
            
            // Determine trust level
            $trustLevel = TrustLevel::fromScore($finalScore);
            
            return new ScoringResult(
                $url,
                $finalScore,
                $trustLevel,
                $confidence,
                $securityResult['score'],
                $reputationResult['score'],
                $complianceResult['score'],
                $detailedMetrics,
                $warnings,
                $errors,
                new DateTime(),
                'aihint-scoring-v1'
            );
            
        } catch (Exception $e) {
            $errors[] = "Scoring failed: " . $e->getMessage();
            return new ScoringResult(
                $url,
                0.0,
                TrustLevel::VERY_LOW,
                0.0,
                0.0,
                0.0,
                0.0,
                [],
                $warnings,
                $errors,
                new DateTime(),
                'aihint-scoring-v1'
            );
        }
    }

    private function scoreSecurityMetrics(string $url): array
    {
        $metrics = [];
        $totalScore = 0.0;
        $count = 0;
        
        // SSL/TLS validation
        try {
            $sslResult = $this->scorers['ssl_tls']->score($url);
            $metrics['ssl_tls'] = $sslResult;
            $totalScore += $sslResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['ssl_tls'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        // Security headers
        try {
            $headersResult = $this->scorers['security_headers']->score($url);
            $metrics['security_headers'] = $headersResult;
            $totalScore += $headersResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['security_headers'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        // Malware checks
        try {
            $malwareResult = $this->scorers['malware']->score($url);
            $metrics['malware'] = $malwareResult;
            $totalScore += $malwareResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['malware'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        return [
            'score' => $count > 0 ? $totalScore / $count : 0.0,
            'metrics' => $metrics
        ];
    }

    private function scoreReputationMetrics(string $url): array
    {
        $metrics = [];
        $totalScore = 0.0;
        $count = 0;
        
        // Domain reputation
        try {
            $reputationResult = $this->scorers['domain_reputation']->score($url);
            $metrics['domain_reputation'] = $reputationResult;
            $totalScore += $reputationResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['domain_reputation'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        // Domain age
        try {
            $ageResult = $this->scorers['domain_age']->score($url);
            $metrics['domain_age'] = $ageResult;
            $totalScore += $ageResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['domain_age'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        // Incidents
        try {
            $incidentsResult = $this->scorers['incidents']->score($url);
            $metrics['incidents'] = $incidentsResult;
            $totalScore += $incidentsResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['incidents'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        return [
            'score' => $count > 0 ? $totalScore / $count : 0.0,
            'metrics' => $metrics
        ];
    }

    private function scoreComplianceMetrics(string $url): array
    {
        $metrics = [];
        $totalScore = 0.0;
        $count = 0;
        
        // Privacy policy
        try {
            $privacyResult = $this->scorers['privacy_policy']->score($url);
            $metrics['privacy_policy'] = $privacyResult;
            $totalScore += $privacyResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['privacy_policy'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        // Contact validation
        try {
            $contactResult = $this->scorers['contact']->score($url);
            $metrics['contact'] = $contactResult;
            $totalScore += $contactResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['contact'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        // Compliance
        try {
            $complianceResult = $this->scorers['compliance']->score($url);
            $metrics['compliance'] = $complianceResult;
            $totalScore += $complianceResult['score'];
            $count++;
        } catch (Exception $e) {
            $metrics['compliance'] = ['score' => 0.0, 'error' => $e->getMessage()];
        }
        
        return [
            'score' => $count > 0 ? $totalScore / $count : 0.0,
            'metrics' => $metrics
        ];
    }

    private function calculateWeightedScore(float $securityScore, float $reputationScore, float $complianceScore): float
    {
        return ($securityScore * $this->weights['security']) +
               ($reputationScore * $this->weights['reputation']) +
               ($complianceScore * $this->weights['compliance']);
    }

    private function calculateConfidence(array $metrics): float
    {
        $totalChecks = 0;
        $successfulChecks = 0;
        
        foreach ($metrics as $category => $categoryMetrics) {
            foreach ($categoryMetrics as $metric => $result) {
                $totalChecks++;
                if (isset($result['score']) && $result['score'] > 0) {
                    $successfulChecks++;
                }
            }
        }
        
        return $totalChecks > 0 ? $successfulChecks / $totalChecks : 0.0;
    }
}
