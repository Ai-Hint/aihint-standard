# Quick Start

This guide will help you get started with AiHint Standard in just a few minutes.

## Prerequisites

Before you begin, make sure you have:

1. **Chosen your implementation** - [Select Python, JavaScript, or PHP](choose-implementation.md)
2. **Basic programming knowledge** in your chosen language
3. **A website or domain** where you want to add AiHint metadata

## Step 1: Install Your Implementation

### Python
```bash
pip install aihint
```

### JavaScript/Node.js
```bash
npm install aihint-js
```

### PHP
```bash
composer require aihint/aihint-php
php vendor/bin/aihint generate-keys --output-dir ./keys
```

## Step 2: Generate Keys (Optional)

For self-signing, you'll need cryptographic keys:

### Python
```bash
aihint generate-keys --output-dir ./keys
```

### JavaScript
```bash
npx aihint generate-keys --output-dir ./keys
```

### PHP
```php
<?php
require_once 'vendor/autoload.php';

use AiHint\KeyManager;

$keyManager = new KeyManager();
$keyManager->generateKeys('./keys');
?>
```

## Step 3: Create Your First AiHint

### Python
```python
from aihint import AiHint

# Create AiHint metadata
aihint = AiHint(
    target="https://example.com",
    issuer="https://example.com",
    score=0.85,
    method="aihint-core-v1"
)

# Sign with your private key
aihint.sign("keys/private_key.pem")

# Save to file
aihint.save("aihint.json")
```

### JavaScript
```javascript
const { AiHint } = require('aihint-js');

// Create AiHint metadata
const aihint = new AiHint({
    target: "https://example.com",
    issuer: "https://example.com",
    score: 0.85,
    method: "aihint-core-v1"
});

// Sign with your private key
aihint.sign("keys/private_key.pem");

// Save to file
aihint.save("aihint.json");
```

### PHP
```php
<?php
require_once 'vendor/autoload.php';

use AiHint\AiHint;

// Create AiHint metadata
$aihint = new AiHint([
    'target' => 'https://example.com',
    'issuer' => 'https://example.com',
    'score' => 0.85,
    'method' => 'aihint-core-v1'
]);

// Sign with your private key
$aihint->sign('keys/private_key.pem');

// Save to file
$aihint->save('aihint.json');
?>
```

## Step 4: Deploy to Your Website

Place the generated `aihint.json` file at:
```
https://yourdomain.com/.well-known/aihint.json
```

## Step 5: Verify Your Implementation

### Python
```bash
aihint verify https://yourdomain.com/.well-known/aihint.json
```

### JavaScript
```bash
npx aihint verify https://yourdomain.com/.well-known/aihint.json
```

### PHP
```bash
php vendor/bin/aihint verify https://yourdomain.com/.well-known/aihint.json
```

## What's Next?

- **[Installation Guide](installation.md)** - Detailed setup instructions
- **[Key Concepts](key-concepts.md)** - Understand the fundamentals
- **[Implementation Guide](../user-guide/implementation-guide.md)** - Advanced usage examples
- **[API Reference](../api-reference/python-api.md)** - Complete API documentation

## Need Help?

- Check the [FAQ](../technical/faq.md) for common questions
- Review the [Implementation Guide](../user-guide/implementation-guide.md) for detailed examples
- See the [Technical Reference](../technical/protocol.md) for protocol details 