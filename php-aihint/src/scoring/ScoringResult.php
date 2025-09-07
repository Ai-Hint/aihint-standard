<?php
namespace AIHint\Scoring;

use DateTime;

class ScoringResult
{
    public string $url;
    public float $finalScore;
    public TrustLevel $trustLevel;
    public float $confidence;
    public float $securityScore;
    public float $reputationScore;
    public float $complianceScore;
    public array $detailedMetrics;
    public array $warnings;
    public array $errors;
    public DateTime $timestamp;
    public string $method;

    public function __construct(
        string $url,
        float $finalScore,
        TrustLevel $trustLevel,
        float $confidence,
        float $securityScore,
        float $reputationScore,
        float $complianceScore,
        array $detailedMetrics,
        array $warnings,
        array $errors,
        DateTime $timestamp,
        string $method = 'aihint-scoring-v1'
    ) {
        $this->url = $url;
        $this->finalScore = $finalScore;
        $this->trustLevel = $trustLevel;
        $this->confidence = $confidence;
        $this->securityScore = $securityScore;
        $this->reputationScore = $reputationScore;
        $this->complianceScore = $complianceScore;
        $this->detailedMetrics = $detailedMetrics;
        $this->warnings = $warnings;
        $this->errors = $errors;
        $this->timestamp = $timestamp;
        $this->method = $method;
    }

    public function toArray(): array
    {
        return [
            'url' => $this->url,
            'final_score' => $this->finalScore,
            'trust_level' => $this->trustLevel->name,
            'trust_level_description' => $this->trustLevel->getDescription(),
            'confidence' => $this->confidence,
            'security_score' => $this->securityScore,
            'reputation_score' => $this->reputationScore,
            'compliance_score' => $this->complianceScore,
            'detailed_metrics' => $this->detailedMetrics,
            'warnings' => $this->warnings,
            'errors' => $this->errors,
            'timestamp' => $this->timestamp->format('c'),
            'method' => $this->method
        ];
    }

    public function toJson(): string
    {
        return json_encode($this->toArray(), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    }

    public function isTrusted(): bool
    {
        return $this->trustLevel->value >= TrustLevel::GOOD->value;
    }

    public function hasErrors(): bool
    {
        return !empty($this->errors);
    }

    public function hasWarnings(): bool
    {
        return !empty($this->warnings);
    }
}
