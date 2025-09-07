<?php
namespace AIHint\Scoring\Metrics;

use DateTime;

abstract class BaseMetrics
{
    protected array $results = [];

    public function addResult(MetricResult $result): void
    {
        $this->results[] = $result;
    }

    public function getResults(): array
    {
        return $this->results;
    }

    public function getSuccessfulResults(): array
    {
        return array_filter($this->results, fn($r) => $r->status === MetricStatus::SUCCESS);
    }

    public function getFailedResults(): array
    {
        return array_filter($this->results, fn($r) => in_array($r->status, [MetricStatus::ERROR, MetricStatus::WARNING]));
    }

    public function getAverageScore(): float
    {
        $successfulResults = $this->getSuccessfulResults();
        if (empty($successfulResults)) {
            return 0.0;
        }

        $totalScore = array_sum(array_map(fn($r) => $r->score, $successfulResults));
        return $totalScore / count($successfulResults);
    }

    public function getTotalExecutionTime(): float
    {
        return array_sum(array_map(fn($r) => $r->executionTimeMs, $this->results));
    }

    public function clear(): void
    {
        $this->results = [];
    }
}
