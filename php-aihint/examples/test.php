<?php
require_once __DIR__ . '/../vendor/autoload.php';

use AIHint\AIHint;
use AIHint\KeyManager;

echo "=== AiHint PHP Implementation Test ===\n\n";

try {
    // Generate keys
    echo "1. Generating keys...\n";
    $keyManager = new KeyManager();
    $keyManager->generateKeys('./keys');
    echo "✓ Keys generated successfully\n\n";

    // Create AiHint
    echo "2. Creating AiHint...\n";
    $aihint = new AIHint([
        'target' => 'https://example.com',
        'issuer' => 'https://example.com',
        'score' => 0.85,
        'method' => 'aihint-core-v1',
        'comment' => 'Test AiHint'
    ]);

    $aihint->sign('./keys/private_key.pem');
    $aihint->save('./aihint.json');
    echo "✓ AiHint created and signed\n\n";

    // Validate
    echo "3. Validating AiHint...\n";
    if ($aihint->validate()) {
        echo "✓ AiHint is valid\n\n";
    } else {
        echo "✗ AiHint validation failed\n\n";
    }

    // Verify
    echo "4. Verifying signature...\n";
    if ($aihint->verify('./keys/public_key.pem')) {
        echo "✓ Signature is valid\n\n";
    } else {
        echo "✗ Signature verification failed\n\n";
    }

    // Load and verify
    echo "5. Loading from file and verifying...\n";
    $loadedAiHint = new AIHint();
    $loadedAiHint->load('./aihint.json');
    
    if ($loadedAiHint->verify('./keys/public_key.pem')) {
        echo "✓ Loaded AiHint signature is valid\n";
        echo "  Target: {$loadedAiHint->target}\n";
        echo "  Score: {$loadedAiHint->score}\n";
        echo "  Issuer: {$loadedAiHint->issuer}\n\n";
    } else {
        echo "✗ Loaded AiHint signature verification failed\n\n";
    }

    echo "=== Test completed successfully ===\n";

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
    exit(1);
}
?> 