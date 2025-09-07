<?php
namespace AIHint\Scoring;

enum TrustLevel: int
{
    case VERY_LOW = 0;
    case LOW = 1;
    case MODERATE = 2;
    case GOOD = 3;
    case HIGH = 4;

    public function getMinScore(): float
    {
        return match($this) {
            self::VERY_LOW => 0.0,
            self::LOW => 0.3,
            self::MODERATE => 0.5,
            self::GOOD => 0.7,
            self::HIGH => 0.9
        };
    }

    public function getMaxScore(): float
    {
        return match($this) {
            self::VERY_LOW => 0.29,
            self::LOW => 0.49,
            self::MODERATE => 0.69,
            self::GOOD => 0.89,
            self::HIGH => 1.0
        };
    }

    public function getDescription(): string
    {
        return match($this) {
            self::VERY_LOW => 'Very low trust (malicious, compromised, or highly suspicious)',
            self::LOW => 'Low trust (multiple red flags, proceed with caution)',
            self::MODERATE => 'Moderate trust (newer sites, some concerns)',
            self::GOOD => 'Good trust (legitimate businesses, established sites)',
            self::HIGH => 'Highly trusted (banks, major corporations, verified entities)'
        };
    }

    public static function fromScore(float $score): self
    {
        if ($score >= 0.9) return self::HIGH;
        if ($score >= 0.7) return self::GOOD;
        if ($score >= 0.5) return self::MODERATE;
        if ($score >= 0.3) return self::LOW;
        return self::VERY_LOW;
    }
}
