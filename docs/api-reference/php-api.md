# PHP API Reference

The PHP implementation of AiHint Standard provides a comprehensive library with CLI support, key generation, and remote key fetching for creating, signing, and verifying AiHint metadata in PHP applications.

**Other implementations**: [Python](python-api.md) | [JavaScript](javascript-api.md)

## Installation

```bash
composer require aihint/aihint-php
```

## Quick Start

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

// Create and sign AiHint metadata
$aihint = new AiHint([
    'target' => 'https://example.com',
    'issuer' => 'https://example.com',
    'score' => 0.85,
    'method' => 'aihint-core-v1'
]);

$aihint->sign('private_key.pem');
$aihint->save('aihint.json');
?>
```

## Core Classes

### AiHint

The main class for creating and managing AiHint metadata.

#### Constructor

```php
new AiHint([
    'target' => string,
    'issuer' => string,
    'score' => float,
    'method' => string,
    'comment' => string,
    'expiresAt' => DateTime
])
```

**Parameters**:
- `target` (string): The target URL for this AiHint
- `issuer` (string): The issuer URL
- `score` (float): Trust score between 0.0 and 1.0
- `method` (string, optional): Scoring method identifier (default: "aihint-core-v1")
- `comment` (string, optional): Additional comment
- `expiresAt` (DateTime, optional): Expiration date

#### Methods

##### `sign(string $privateKeyPath): void`
Sign the AiHint metadata with a private key.

##### `verify(string $publicKeyPath = null): bool`
Verify the signature of the AiHint metadata. If no public key is provided, it will attempt to fetch from the `public_key_url` in the metadata.

##### `save(string $filePath): void`
Save the AiHint metadata to a JSON file.

##### `load(string $filePath): void`
Load AiHint metadata from a JSON file.

##### `validate(): bool`
Validate the AiHint metadata structure.

##### `static fromUrl(string $url): AiHint`
Fetch and load AiHint metadata from a URL.

## Key Management

### KeyManager

Utility class for generating and managing cryptographic keys.

```php
<?php
use AiHint\KeyManager;

// Generate a new key pair
$keyManager = new KeyManager();
$keyManager->generateKeys('keys/');

// Load existing keys
$privateKey = $keyManager->loadPrivateKey('keys/private_key.pem');
$publicKey = $keyManager->loadPublicKey('keys/public_key.pem');

// Fetch remote public key
$remoteKey = $keyManager->fetchRemoteKey('https://example.com/pubkey.pem');
?>
```

## CLI Usage

The PHP implementation includes a command-line interface:

```bash
# Generate keys
php vendor/bin/aihint generate-keys --output-dir ./keys

# Create and sign AiHint
php vendor/bin/aihint create \
  --target "https://example.com" \
  --issuer "https://example.com" \
  --score 0.85 \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"

# Verify AiHint
php vendor/bin/aihint verify aihint.json

# Validate AiHint
php vendor/bin/aihint validate aihint.json

# Fetch from URL
php vendor/bin/aihint fetch https://example.com/.well-known/aihint.json
```

## Examples

### Basic Usage

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

// Create AiHint with expiration
$expiresAt = new DateTime('+1 year');
$aihint = new AiHint([
    'target' => 'https://mywebsite.com',
    'issuer' => 'https://mywebsite.com',
    'score' => 0.92,
    'method' => 'aihint-core-v1',
    'comment' => 'My website trust metadata',
    'expiresAt' => $expiresAt
]);

// Sign and save
$aihint->sign('private_key.pem');
$aihint->save('aihint.json');
?>
```

### Verification with Remote Key Fetching

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

// Load and verify with automatic remote key fetching
$aihint = new AiHint();
$aihint->load('aihint.json');

// The library will automatically fetch the public key from the URL
if ($aihint->verify()) {
    echo "Signature is valid!\n";
    echo "Trust score: " . $aihint->score . "\n";
} else {
    echo "Signature verification failed!\n";
}
?>
```

### Loading from URL

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

try {
    // Fetch AiHint from a URL
    $aihint = AiHint::fromUrl('https://example.com/.well-known/aihint.json');
    
    if ($aihint->validate()) {
        echo "AiHint is valid!\n";
        echo "Target: " . $aihint->target . "\n";
        echo "Score: " . $aihint->score . "\n";
    } else {
        echo "AiHint validation failed!\n";
    }
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

### Batch Processing

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

function processDirectory($directory) {
    $files = glob($directory . '/*.json');
    
    foreach ($files as $filepath) {
        $filename = basename($filepath);
        $aihint = new AiHint();
        
        try {
            $aihint->load($filepath);
            $isValid = $aihint->validate();
            echo "$filename: " . ($isValid ? 'Valid' : 'Invalid') . "\n";
        } catch (Exception $e) {
            echo "$filename: Error - " . $e->getMessage() . "\n";
        }
    }
}

processDirectory('./aihint-files/');
?>
```

## Error Handling

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;
use AiHint\AiHintException;

try {
    $aihint = new AiHint();
    $aihint->load('aihint.json');
    $aihint->verify('public_key.pem');
} catch (AiHintException $e) {
    echo "AiHint error: " . $e->getMessage() . "\n";
} catch (Exception $e) {
    echo "Unexpected error: " . $e->getMessage() . "\n";
}
?>
```

## WordPress Integration

The PHP implementation is designed to work well with WordPress:

```php
<?php
// In your WordPress plugin or theme
require_once 'vendor/autoload.php';

use AiHint\AiHint;

// Create AiHint for your WordPress site
$aihint = new AiHint([
    'target' => get_site_url(),
    'issuer' => get_site_url(),
    'score' => 0.85,
    'method' => 'aihint-core-v1',
    'comment' => 'WordPress site trust metadata'
]);

// Save to .well-known directory
$wellKnownDir = ABSPATH . '.well-known/';
if (!is_dir($wellKnownDir)) {
    mkdir($wellKnownDir, 0755, true);
}

$aihint->sign('private_key.pem');
$aihint->save($wellKnownDir . 'aihint.json');
?>
```

## Configuration

The PHP implementation supports configuration through environment variables:

- `AIHINT_DEFAULT_METHOD`: Default scoring method
- `AIHINT_DEFAULT_EXPIRY_DAYS`: Default expiration period in days
- `AIHINT_KEY_DIRECTORY`: Default directory for key files
- `AIHINT_TIMEOUT`: HTTP timeout for remote fetching (default: 30 seconds)
- `AIHINT_CACHE_DIR`: Directory for caching remote keys (default: `./cache`)

## Advanced Features

### Enhanced Schema Validation

The PHP implementation includes enhanced schema validation with detailed error messages:

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;
use AiHint\ValidationException;

try {
    $aihint = new AiHint([
        'target' => 'https://example.com',
        'issuer' => 'https://example.com',
        'score' => 1.5  // Invalid: score > 1.0
    ]);
} catch (ValidationException $e) {
    echo "Validation error: " . $e->getMessage() . "\n";
    echo "Field: " . $e->getField() . "\n";
    echo "Value: " . $e->getValue() . "\n";
}
?>
```

### Remote Key Fetching with Caching

Automatically fetch and cache public keys from URLs:

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;
use AiHint\KeyManager;

// The library will automatically fetch and cache remote keys
$aihint = new AiHint();
$aihint->load("aihint.json");

// This will fetch the public key from the URL and cache it
$isValid = $aihint->verify();

echo $isValid ? "Valid!" : "Invalid!";
?>
```

### Custom Validation

You can add custom validation rules:

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

class CustomAiHint extends AiHint {
    protected function validateScore($score) {
        parent::validateScore($score);
        
        // Custom validation: score must be at least 0.5
        if ($score < 0.5) {
            throw new ValidationException('Score must be at least 0.5');
        }
    }
}

$aihint = new CustomAiHint([
    'target' => 'https://example.com',
    'issuer' => 'https://example.com',
    'score' => 0.3  // This will throw an error
]);
?>
```

## Performance Considerations

For high-traffic applications, consider caching verified AiHint metadata:

```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

class AiHintCache {
    private $cache = [];
    
    public function getVerifiedAiHint($url) {
        if (isset($this->cache[$url])) {
            return $this->cache[$url];
        }
        
        $aihint = AiHint::fromUrl($url);
        if ($aihint->verify()) {
            $this->cache[$url] = $aihint;
            return $aihint;
        }
        
        return null;
    }
}

$cache = new AiHintCache();
$aihint = $cache->getVerifiedAiHint('https://example.com/.well-known/aihint.json');
?>
```

## See Also

- [Python API](python-api.md) - Python implementation
- [JavaScript API](javascript-api.md) - Node.js implementation
- [CLI Reference](cli-reference.md) - Command-line interface
- [Implementation Guide](../user-guide/implementation-guide.md) - Detailed usage guide 