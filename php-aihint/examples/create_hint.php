<?php
require_once __DIR__ . '/../src/AIHint.php';
use AIHint\AIHint;

$hint = [
    "version" => "0.1",
    "type" => "global",
    "target" => "https://example.com",
    "issuer" => "https://trust.aihint.org",
    "score" => 0.92,
    "method" => "aihint-core-v1",
    "issued_at" => "2025-01-01T12:00:00Z",
    "expires_at" => "2026-01-01T00:00:00Z",
    "comment" => "Example AiHint for demonstration",
    "public_key_url" => "https://trust.aihint.org/pubkey.pem"
];

$signed = AIHint::signHint($hint, 'private_key.pem');
file_put_contents('aihint.json', json_encode($signed, JSON_PRETTY_PRINT));
echo "Signed:\n" . json_encode($signed, JSON_PRETTY_PRINT) . "\n";

$valid = AIHint::verifyHint($signed, 'public_key.pem');
echo "Signature valid? " . ($valid ? 'true' : 'false') . "\n";

$schemaValid = AIHint::validateHint($signed);
echo "Schema valid? " . ($schemaValid ? 'true' : 'false') . "\n";
