<?php
require_once __DIR__ . '/../vendor/autoload.php';

use AIHint\AIHint;
use AIHint\Scoring\TrustScoringEngine;

echo "=== AiHint Generation with Trust Scoring ===\n\n";

// Initialize the trust scoring engine
$scoringEngine = new TrustScoringEngine();

// URLs to score and create AiHints for
$urls = [
    'https://github.com',
    'https://stackoverflow.com',
    'https://example.com'
];

foreach ($urls as $url) {
    echo "Processing: $url\n";
    echo str_repeat('-', 50) . "\n";
    
    try {
        // Get trust score
        $result = $scoringEngine->scoreWebsite($url);
        
        // Create AiHint data structure
        $aihintData = [
            'version' => '0.1',
            'type' => 'global',
            'target' => $url,
            'issuer' => 'https://trust.aihint.org',
            'score' => $result->finalScore,
            'method' => 'aihint-scoring-v1', // Use scoring method
            'issued_at' => (new DateTime())->format('c'),
            'expires_at' => (new DateTime('+1 year'))->format('c'),
            'comment' => "Trust score: {$result->finalScore} (Level: {$result->trustLevel->name})",
            'public_key_url' => 'https://trust.aihint.org/pubkey.pem'
        ];
        
        // Create AiHint object
        $aihint = new AIHint($aihintData);
        
        // Validate the AiHint
        $isValid = $aihint->validate();
        echo "AiHint valid: " . ($isValid ? 'YES' : 'NO') . "\n";
        
        // Display the AiHint data
        echo "Score: {$result->finalScore}\n";
        echo "Trust Level: {$result->trustLevel->name}\n";
        echo "Security Score: {$result->securityScore}\n";
        echo "Reputation Score: {$result->reputationScore}\n";
        echo "Compliance Score: {$result->complianceScore}\n";
        
        // Save to file
        $filename = 'aihint_' . parse_url($url, PHP_URL_HOST) . '.json';
        $aihint->save($filename);
        echo "Saved to: $filename\n";
        
        // Display JSON structure
        echo "\nAiHint JSON:\n";
        echo json_encode($aihint->toArray(), JSON_PRETTY_PRINT) . "\n";
        
    } catch (Exception $e) {
        echo "Error processing $url: " . $e->getMessage() . "\n";
    }
    
    echo "\n" . str_repeat('=', 70) . "\n\n";
}

echo "Done! Generated AiHint files for all URLs.\n";
