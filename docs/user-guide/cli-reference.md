# CLI Reference

The AIHint command-line interface provides easy access to all AIHint functionality.

## Commands Overview

```bash
aihint --help
```

## Commands

### `aihint create`

Create a new AIHint metadata file.

**Options:**
- `--target` - Target domain URL (required)
- `--issuer` - Issuing authority URL (required)
- `--score` - Trust score 0.0-1.0 (required)
- `--method` - Scoring method used (required)
- `--public-key-url` - Public key URL (required)
- `--expires-in` - Expiration in days (default: 365)
- `--comment` - Optional comment
- `--output` - Output file path
- `--private-key` - Private key file for signing
- `--version` - AIHint version (default: 0.1)

**Example:**
```bash
aihint create \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --score 0.92 \
  --method "aihint-core-v1" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --private-key "private_key.pem" \
  --output "aihint.json"
```

### `aihint validate`

Validate an AIHint metadata file.

**Usage:**
```bash
aihint validate <file_path>
```

**Example:**
```bash
aihint validate aihint.json
```

### `aihint verify`

Verify an AIHint metadata file signature.

**Usage:**
```bash
aihint verify <file_path>
```

**Example:**
```bash
aihint verify aihint.json
```

### `aihint info`

Display information about an AIHint metadata file.

**Usage:**
```bash
aihint info <file_path>
```

**Example:**
```bash
aihint info aihint.json
```

**Output:**
```
AIHint Information:
  Version: 0.1
  Type: global
  Target: https://example.com
  Issuer: https://trust.aihint.org
  Score: 0.92
  Method: aihint-core-v1
  Issued: 2025-01-01T12:00:00Z
  Expires: 2026-01-01T00:00:00Z
  Comment: Example AIHint
  Status: Valid (365 days left)
```

### `aihint sign`

Sign an existing AIHint metadata file.

**Usage:**
```bash
aihint sign <file_path> --private-key <key_path>
```

**Example:**
```bash
aihint sign aihint.json --private-key private_key.pem
```

## Global Options

- `--help` - Show help message
- `--version` - Show version and exit

## Exit Codes

- `0` - Success
- `1` - Error (with error message)
- `2` - Usage error (invalid arguments) 