<?php
namespace AIHint\Scoring\Scorers;

use AIHint\Scoring\Metrics\MetricResult;
use AIHint\Scoring\Metrics\MetricStatus;
use DateTime;
use Exception;

abstract class BaseScorer
{
    protected array $config;
    protected int $timeout;

    public function __construct(array $config = [])
    {
        $this->config = $config;
        $this->timeout = $config['timeout'] ?? 10;
    }

    abstract public function score(string $url): array;

    protected function makeRequest(string $url, array $options = []): string
    {
        $context = stream_context_create([
            'http' => array_merge([
                'timeout' => $this->timeout,
                'user_agent' => 'AiHint-PHP-Scoring/1.0',
                'follow_location' => true,
                'max_redirects' => 5
            ], $options)
        ]);

        $result = file_get_contents($url, false, $context);
        
        if ($result === false) {
            throw new Exception("Failed to fetch URL: $url");
        }

        return $result;
    }

    protected function parseUrl(string $url): array
    {
        $parsed = parse_url($url);
        if ($parsed === false) {
            throw new Exception("Invalid URL: $url");
        }
        
        return $parsed;
    }

    protected function getDomain(string $url): string
    {
        $parsed = $this->parseUrl($url);
        return $parsed['host'] ?? '';
    }

    protected function isHttps(string $url): bool
    {
        $parsed = $this->parseUrl($url);
        return ($parsed['scheme'] ?? '') === 'https';
    }

    protected function createResult(
        string $name,
        float $score,
        MetricStatus $status,
        string $message = '',
        array $details = [],
        float $executionTimeMs = 0.0
    ): MetricResult {
        return new MetricResult(
            $name,
            $score,
            $status,
            $message,
            $details,
            new DateTime(),
            $executionTimeMs
        );
    }

    protected function measureExecutionTime(callable $callback): array
    {
        $startTime = microtime(true);
        $result = $callback();
        $endTime = microtime(true);
        $executionTime = ($endTime - $startTime) * 1000; // Convert to milliseconds
        
        return [$result, $executionTime];
    }
}
