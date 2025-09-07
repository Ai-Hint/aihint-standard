<?php
require_once __DIR__ . '/../src/scoring/index.php';

use AIHint\Scoring\TrustScoringEngine;
use AIHint\Scoring\ScoringResult;

echo "AiHint Trust Scoring System - PHP Example\n";
echo "========================================\n\n";

// Example 1: Basic scoring
echo "Example 1: Basic Website Scoring\n";
echo "--------------------------------\n";

try {
    $engine = new TrustScoringEngine();
    $result = $engine->scoreWebsite('https://github.com');
    
    echo "URL: " . $result->url . "\n";
    echo "Trust Score: " . number_format($result->finalScore, 3) . "\n";
    echo "Trust Level: " . $result->trustLevel->name . "\n";
    echo "Confidence: " . number_format($result->confidence, 3) . "\n";
    echo "Security Score: " . number_format($result->securityScore, 3) . "\n";
    echo "Reputation Score: " . number_format($result->reputationScore, 3) . "\n";
    echo "Compliance Score: " . number_format($result->complianceScore, 3) . "\n";
    
    if (!empty($result->warnings)) {
        echo "\nWarnings:\n";
        foreach ($result->warnings as $warning) {
            echo "  - $warning\n";
        }
    }
    
    if (!empty($result->errors)) {
        echo "\nErrors:\n";
        foreach ($result->errors as $error) {
            echo "  - $error\n";
        }
    }
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

echo "\n" . str_repeat('=', 50) . "\n\n";

// Example 2: Custom configuration
echo "Example 2: Custom Configuration\n";
echo "-------------------------------\n";

$customConfig = [
    'ssl' => [
        'timeout' => 15
    ],
    'headers' => [
        'timeout' => 15
    ],
    'malware' => [
        'timeout' => 15,
        'google_safe_browsing' => [
            'enabled' => false, // Set to true and add API key for real checks
            'api_key' => 'YOUR_API_KEY_HERE'
        ],
        'virustotal' => [
            'enabled' => false, // Set to true and add API key for real checks
            'api_key' => 'YOUR_API_KEY_HERE'
        ],
        'phishtank' => [
            'enabled' => true // Free service
        ]
    ],
    'weights' => [
        'security' => 0.5,      // 50% weight for security
        'reputation' => 0.3,    // 30% weight for reputation
        'compliance' => 0.2     // 20% weight for compliance
    ]
];

try {
    $engine = new TrustScoringEngine($customConfig);
    $result = $engine->scoreWebsite('https://stackoverflow.com');
    
    echo "URL: " . $result->url . "\n";
    echo "Trust Score: " . number_format($result->finalScore, 3) . "\n";
    echo "Trust Level: " . $result->trustLevel->name . "\n";
    echo "Method: " . $result->method . "\n";
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

echo "\n" . str_repeat('=', 50) . "\n\n";

// Example 3: Batch scoring
echo "Example 3: Batch Scoring\n";
echo "------------------------\n";

$urls = [
    'https://github.com',
    'https://stackoverflow.com',
    'https://example.com'
];

$results = [];

foreach ($urls as $url) {
    try {
        echo "Scoring: $url\n";
        $result = $engine->scoreWebsite($url);
        $results[] = [
            'url' => $result->url,
            'score' => $result->finalScore,
            'level' => $result->trustLevel->name,
            'confidence' => $result->confidence
        ];
    } catch (Exception $e) {
        echo "  Error: " . $e->getMessage() . "\n";
        $results[] = [
            'url' => $url,
            'score' => 0.0,
            'level' => 'ERROR',
            'confidence' => 0.0
        ];
    }
}

echo "\nBatch Results:\n";
foreach ($results as $result) {
    echo sprintf("%-30s | Score: %5.3f | Level: %-10s | Confidence: %5.3f\n",
        $result['url'],
        $result['score'],
        $result['level'],
        $result['confidence']
    );
}

echo "\n" . str_repeat('=', 50) . "\n\n";

// Example 4: JSON output
echo "Example 4: JSON Output\n";
echo "----------------------\n";

try {
    $result = $engine->scoreWebsite('https://github.com');
    echo $result->toJson() . "\n";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

echo "\nDone!\n";
