# CLI Reference

AiHint Standard provides command-line interfaces for all implementations to make it easy to work with AiHint metadata from the terminal.

## Python CLI

### Installation
```bash
pip install aihint
```

### Commands

#### Generate Keys
```bash
aihint generate-keys --output-dir ./keys
```

**Options**:
- `--output-dir`: Directory to save generated keys (default: current directory)

#### Create AiHint
```bash
aihint create \
  --target "https://example.com" \
  --issuer "https://example.com" \
  --score 0.85 \
  --method "aihint-core-v1" \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"
```

**Options**:
- `--target`: Target URL for the AiHint
- `--issuer`: Issuer URL
- `--score`: Trust score (0.0-1.0)
- `--method`: Scoring method (default: "aihint-core-v1")
- `--comment`: Optional comment
- `--expires-at`: Expiration date (ISO format)
- `--private-key`: Path to private key file
- `--output`: Output file path

#### Verify AiHint
```bash
aihint verify aihint.json
aihint verify https://example.com/.well-known/aihint.json
```

**Options**:
- `--public-key`: Path to public key file (optional)

#### Validate AiHint
```bash
aihint validate aihint.json
```

#### Show Info
```bash
aihint info aihint.json
```

#### Create with Automated Scoring
```bash
aihint create-with-score \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --private-key "keys/private_key.pem" \
  --verbose \
  --output "scored_aihint.json"
```

**Options**:
- `--target`: Target URL to score and create AiHint for
- `--issuer`: Issuer URL
- `--public-key-url`: Public key URL for verification
- `--expires-in`: Expiration in days (default: 365)
- `--comment`: Optional comment
- `--output`: Output file path
- `--private-key`: Private key file for signing
- `--version`: AIHint version (default: 0.1)
- `--config`: Scoring configuration file path
- `--verbose`: Verbose output with detailed scoring breakdown

#### Trust Scoring Commands
```bash
# Score a single website
aihint scoring score https://example.com

# Score multiple websites
aihint scoring batch --urls https://example.com,https://github.com

# Generate sample configuration
aihint scoring config --output scoring_config.json
```

**Scoring Options**:
- `--format`: Output format (text, table, json)
- `--config`: Configuration file path
- `--verbose`: Detailed output
- `--timeout`: Request timeout in seconds

---

## JavaScript CLI

### Installation
```bash
npm install aihint-js
```

### Commands

#### Generate Keys
```bash
npx aihint generate-keys --output-dir ./keys
```

**Options**:
- `--output-dir`: Directory to save generated keys (default: current directory)

#### Create AiHint
```bash
npx aihint create \
  --target "https://example.com" \
  --issuer "https://example.com" \
  --score 0.85 \
  --method "aihint-core-v1" \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"
```

**Options**:
- `--target`: Target URL for the AiHint
- `--issuer`: Issuer URL
- `--score`: Trust score (0.0-1.0)
- `--method`: Scoring method (default: "aihint-core-v1")
- `--comment`: Optional comment
- `--expires-at`: Expiration date (ISO format)
- `--private-key`: Path to private key file
- `--output`: Output file path

#### Verify AiHint
```bash
npx aihint verify aihint.json
npx aihint verify https://example.com/.well-known/aihint.json
```

**Options**:
- `--public-key`: Path to public key file (optional, will fetch from URL if not provided)

#### Validate AiHint
```bash
npx aihint validate aihint.json
```

#### Fetch from URL
```bash
npx aihint fetch https://example.com/.well-known/aihint.json
```

#### Show Info
```bash
npx aihint info aihint.json
```

---

## PHP CLI

### Installation
```bash
composer require aihint/aihint-php
```

### Commands

#### Generate Keys
```bash
php vendor/bin/aihint generate-keys --output-dir ./keys
```

**Options**:
- `--output-dir`: Directory to save generated keys (default: current directory)

#### Create AiHint
```bash
php vendor/bin/aihint create \
  --target "https://example.com" \
  --issuer "https://example.com" \
  --score 0.85 \
  --method "aihint-core-v1" \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"
```

**Options**:
- `--target`: Target URL for the AiHint
- `--issuer`: Issuer URL
- `--score`: Trust score (0.0-1.0)
- `--method`: Scoring method (default: "aihint-core-v1")
- `--comment`: Optional comment
- `--expires-at`: Expiration date (ISO format)
- `--private-key`: Path to private key file
- `--output`: Output file path

#### Verify AiHint
```bash
php vendor/bin/aihint verify aihint.json
php vendor/bin/aihint verify https://example.com/.well-known/aihint.json
```

**Options**:
- `--public-key`: Path to public key file (optional, will fetch from URL if not provided)

#### Validate AiHint
```bash
php vendor/bin/aihint validate aihint.json
```

#### Fetch from URL
```bash
php vendor/bin/aihint fetch https://example.com/.well-known/aihint.json
```

#### Show Info
```bash
php vendor/bin/aihint info aihint.json
```

---

## Common Use Cases

### Quick Setup
```bash
# Generate keys
aihint generate-keys --output-dir ./keys

# Create and sign AiHint (manual scoring)
aihint create \
  --target "https://mywebsite.com" \
  --issuer "https://mywebsite.com" \
  --score 0.85 \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"

# OR create with automated scoring
aihint create-with-score \
  --target "https://mywebsite.com" \
  --issuer "https://trust.aihint.org" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --private-key "keys/private_key.pem" \
  --verbose \
  --output "scored_aihint.json"

# Verify the result
aihint verify aihint.json
```

### Automated Scoring Workflows
```bash
# Score a single website
aihint scoring score https://example.com --verbose

# Score multiple websites with batch processing
aihint scoring batch --urls https://example.com,https://github.com,https://stackoverflow.com

# Generate scoring configuration
aihint scoring config --output my_scoring_config.json

# Create AiHint with custom scoring configuration
aihint create-with-score \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --config my_scoring_config.json \
  --verbose \
  --output "custom_scored_aihint.json"
```

### Batch Processing
```bash
# Validate all AiHint files in a directory
for file in *.json; do
  aihint validate "$file"
done

# Score multiple websites and create AiHints
for url in https://example.com https://github.com https://stackoverflow.com; do
  aihint create-with-score \
    --target "$url" \
    --issuer "https://trust.aihint.org" \
    --public-key-url "https://trust.aihint.org/pubkey.pem" \
    --output "$(basename $url)_aihint.json"
done
```

### Remote Verification
```bash
# Verify AiHint from a remote URL
aihint verify https://example.com/.well-known/aihint.json
```

### Key Management
```bash
# Generate new keys
aihint generate-keys --output-dir ./new-keys

# Backup existing keys
cp keys/private_key.pem backup/private_key_$(date +%Y%m%d).pem
cp keys/public_key.pem backup/public_key_$(date +%Y%m%d).pem
```

## Environment Variables

All CLI implementations support the following environment variables:

- `AIHINT_DEFAULT_METHOD`: Default scoring method
- `AIHINT_DEFAULT_EXPIRY_DAYS`: Default expiration period in days
- `AIHINT_KEY_DIRECTORY`: Default directory for key files
- `AIHINT_TIMEOUT`: HTTP timeout for remote operations (JavaScript/PHP only)
- `AIHINT_CACHE_DIR`: Directory for caching remote keys (PHP only)

## See Also

- [Python API](python-api.md) - Python implementation details
- [JavaScript API](javascript-api.md) - JavaScript implementation details
- [PHP API](php-api.md) - PHP implementation details
- [Implementation Guide](../user-guide/implementation-guide.md) - Detailed usage guide 