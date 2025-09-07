<?php
namespace AIHint\Scoring\Metrics;

use DateTime;

class MetricResult
{
    public string $name;
    public float $score;
    public MetricStatus $status;
    public string $message;
    public array $details;
    public DateTime $timestamp;
    public float $executionTimeMs;

    public function __construct(
        string $name,
        float $score,
        MetricStatus $status,
        string $message = '',
        array $details = [],
        ?DateTime $timestamp = null,
        float $executionTimeMs = 0.0
    ) {
        $this->name = $name;
        $this->score = $score;
        $this->status = $status;
        $this->message = $message;
        $this->details = $details;
        $this->timestamp = $timestamp ?? new DateTime();
        $this->executionTimeMs = $executionTimeMs;
    }

    public function toArray(): array
    {
        return [
            'name' => $this->name,
            'score' => $this->score,
            'status' => $this->status->value,
            'message' => $this->message,
            'details' => $this->details,
            'timestamp' => $this->timestamp->format('c'),
            'execution_time_ms' => $this->executionTimeMs
        ];
    }
}
