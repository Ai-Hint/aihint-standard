# JavaScript API Reference

The JavaScript/Node.js implementation of AiHint Standard provides a comprehensive library with TypeScript support for creating, signing, and verifying AiHint metadata, including **automated trust scoring** capabilities.

**Other implementations**: [Python](python-api.md) | [PHP](php-api.md)

## Installation

```bash
npm install aihint-js
```

## Quick Start

```javascript
const { AiHint } = require('aihint-js');

// Create and sign AiHint metadata
const aihint = new AiHint({
    target: "https://example.com",
    issuer: "https://example.com",
    score: 0.85,
    method: "aihint-core-v1"
});

aihint.sign("private_key.pem");
aihint.save("aihint.json");
```

## Trust Scoring

The JavaScript implementation includes a modern trust scoring system:

```javascript
const { TrustScoringEngine } = require('aihint-js/scoring');

// Initialize the scoring engine
const engine = new TrustScoringEngine();

// Score a website
const result = await engine.scoreWebsite("https://example.com");

console.log(`Trust Score: ${result.finalScore.toFixed(3)}`);
console.log(`Trust Level: ${result.trustLevel}`);
console.log(`Confidence: ${result.confidence.toFixed(3)}`);
```

### CLI Usage

```bash
# Score a single website
npx aihint-scoring score https://example.com

# Score multiple websites
npx aihint-scoring batch https://example.com https://github.com

# Build scoring system
npm run build:scoring
```

## Core Classes

### AiHint

The main class for creating and managing AiHint metadata.

#### Constructor

```javascript
new AiHint({
    target: string,
    issuer: string,
    score: number,
    method?: string,
    comment?: string,
    expiresAt?: Date
})
```

**Parameters**:
- `target` (string): The target URL for this AiHint
- `issuer` (string): The issuer URL
- `score` (number): Trust score between 0.0 and 1.0
- `method` (string, optional): Scoring method identifier (default: "aihint-core-v1")
- `comment` (string, optional): Additional comment
- `expiresAt` (Date, optional): Expiration date

#### Methods

##### `sign(privateKeyPath: string): Promise<void>`
Sign the AiHint metadata with a private key.

##### `verify(publicKeyPath?: string): Promise<boolean>`
Verify the signature of the AiHint metadata.

##### `save(filePath: string): Promise<void>`
Save the AiHint metadata to a JSON file.

##### `load(filePath: string): Promise<void>`
Load AiHint metadata from a JSON file.

##### `validate(): boolean`
Validate the AiHint metadata structure.

##### `fetchFromUrl(url: string): Promise<AiHint>`
Fetch and load AiHint metadata from a URL.

## Key Management

### KeyManager

Utility class for generating and managing cryptographic keys.

```javascript
const { KeyManager } = require('aihint-js');

// Generate a new key pair
const keyManager = new KeyManager();
await keyManager.generateKeys("keys/");

// Load existing keys
const privateKey = await keyManager.loadPrivateKey("keys/private_key.pem");
const publicKey = await keyManager.loadPublicKey("keys/public_key.pem");
```

## CLI Usage

The JavaScript implementation includes a command-line interface:

```bash
# Generate keys
npx aihint generate-keys --output-dir ./keys

# Create and sign AiHint
npx aihint create \
  --target "https://example.com" \
  --issuer "https://example.com" \
  --score 0.85 \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"

# Verify AiHint
npx aihint verify aihint.json

# Validate AiHint
npx aihint validate aihint.json

# Fetch from URL
npx aihint fetch https://example.com/.well-known/aihint.json
```

## TypeScript Support

The library includes full TypeScript support:

```typescript
import { AiHint, AiHintOptions } from 'aihint-js';

interface CustomAiHintOptions extends AiHintOptions {
    customField?: string;
}

const options: CustomAiHintOptions = {
  target: "https://example.com",
    issuer: "https://example.com",
    score: 0.85,
    customField: "custom value"
};

const aihint = new AiHint(options);
```

## Examples

### Basic Usage

```javascript
const { AiHint } = require('aihint-js');

async function createAiHint() {
    const aihint = new AiHint({
        target: "https://mywebsite.com",
        issuer: "https://mywebsite.com",
        score: 0.92,
        method: "aihint-core-v1",
        comment: "My website trust metadata"
    });

    await aihint.sign("private_key.pem");
    await aihint.save("aihint.json");
}

createAiHint().catch(console.error);
```

### Verification

```javascript
const { AiHint } = require('aihint-js');

async function verifyAiHint() {
    const aihint = new AiHint();
    await aihint.load("aihint.json");

    const isValid = await aihint.verify("public_key.pem");
    
    if (isValid) {
        console.log("Signature is valid!");
        console.log(`Trust score: ${aihint.score}`);
    } else {
        console.log("Signature verification failed!");
    }
}

verifyAiHint().catch(console.error);
```

### Remote Key Fetching

```javascript
const { AiHint } = require('aihint-js');

async function verifyWithRemoteKey() {
    const aihint = new AiHint();
    await aihint.load("aihint.json");

    // The library will automatically fetch the public key from the URL
    const isValid = await aihint.verify();
    
    console.log(isValid ? "Valid!" : "Invalid!");
}

verifyWithRemoteKey().catch(console.error);
```

### Batch Processing

```javascript
const { AiHint } = require('aihint-js');
const fs = require('fs').promises;
const path = require('path');

async function processDirectory(directory) {
    const files = await fs.readdir(directory);
    
    for (const filename of files) {
        if (filename.endsWith('.json')) {
            const filepath = path.join(directory, filename);
            const aihint = new AiHint();
            
            try {
                await aihint.load(filepath);
                const isValid = aihint.validate();
                console.log(`${filename}: ${isValid ? 'Valid' : 'Invalid'}`);
            } catch (error) {
                console.log(`${filename}: Error - ${error.message}`);
            }
        }
    }
}

processDirectory('./aihint-files/').catch(console.error);
```

## Error Handling

```javascript
const { AiHint, AiHintError } = require('aihint-js');

async function handleErrors() {
    try {
        const aihint = new AiHint();
        await aihint.load("aihint.json");
        await aihint.verify("public_key.pem");
    } catch (error) {
        if (error instanceof AiHintError) {
            console.log(`AiHint error: ${error.message}`);
        } else {
            console.log(`Unexpected error: ${error.message}`);
        }
    }
}

handleErrors();
```

## Configuration

The JavaScript implementation supports configuration through environment variables:

- `AIHINT_DEFAULT_METHOD`: Default scoring method
- `AIHINT_DEFAULT_EXPIRY_DAYS`: Default expiration period in days
- `AIHINT_KEY_DIRECTORY`: Default directory for key files
- `AIHINT_TIMEOUT`: HTTP timeout for remote key fetching (default: 5000ms)

## Advanced Features

### Enhanced Schema Validation

The JavaScript implementation includes enhanced schema validation with detailed error messages:

```javascript
const { AiHint, ValidationError } = require('aihint-js');

try {
    const aihint = new AiHint({
        target: "https://example.com",
        issuer: "https://example.com",
        score: 1.5  // Invalid: score > 1.0
    });
} catch (error) {
    if (error instanceof ValidationError) {
        console.log(`Validation error: ${error.message}`);
        console.log(`Field: ${error.field}`);
        console.log(`Value: ${error.value}`);
    }
}
```

### Remote Key Fetching

Automatically fetch public keys from URLs:

```javascript
const { AiHint } = require('aihint-js');

async function verifyWithRemoteKey() {
    const aihint = new AiHint();
    await aihint.load("aihint.json");
    
    // The public key URL is stored in the AiHint metadata
    // The library will automatically fetch it for verification
    const isValid = await aihint.verify();
    
    console.log(isValid ? "Valid!" : "Invalid!");
}
```

## See Also

- [Python API](python-api.md) - Python implementation
- [PHP API](php-api.md) - PHP implementation
- [CLI Reference](cli-reference.md) - Command-line interface
- [Implementation Guide](../user-guide/implementation-guide.md) - Detailed usage guide 