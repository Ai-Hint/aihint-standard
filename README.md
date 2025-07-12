> **⚠️ Important Notice: Open Source vs. Official Issuer**
>
> This open source AiHint project provides the protocol, libraries, and tools for learning, development, testing, and self-signed metadata.
>
> **Self-signed AiHint metadata is not globally trusted by default.**
>
> For production, public, or commercial use—where global trust and official verification are required—please use the AiHint Official Issuer Service (coming soon), which provides domain validation, billing, and a globally recognized trust authority.
>
> **Use this open source project for:**
> - Experimentation and learning
> - Local development and testing
> - Self-hosted or private use
>
> **Use the Official Issuer Service for:**
> - Production and public-facing websites
> - Globally trusted AiHint metadata
> - Verified issuer status and support

# AiHint Standard

**AiHint** is an open standard to expose signed, verifiable metadata for websites, intended to be read by AI systems, LLMs, and intelligent agents.

## Purpose

Allow any AI system to:
- Discover a well-known, machine-readable JSON file on a website
- Verify its cryptographic signature
- Understand the site's declared trust score and metadata

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/Ai-Hint/aihint-standard.git
cd aihint-standard
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Create Your First AiHint

```bash
# Create a signed AiHint metadata file
aihint create \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --score 0.92 \
  --method "aihint-core-v1" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --private-key "private_key.pem" \
  --output "aihint.json"
```

### Validate and Verify

```bash
# Validate an AiHint file
aihint validate aihint.json

# Verify the signature
aihint verify aihint.json

# Get detailed information
aihint info aihint.json
```

## Python API

```python
from aihint import AIHint
from datetime import datetime, timezone, timedelta

# Create AIHint instance
aihint = AIHint()

# Create a new hint
expires_at = datetime.now(timezone.utc) + timedelta(days=365)
hint = aihint.create_global_hint(
    target="https://example.com",
    issuer="https://trust.aihint.org",
    score=0.92,
    method="aihint-core-v1",
    public_key_url="https://trust.aihint.org/pubkey.pem",
    expires_at=expires_at,
    comment="My website trust metadata"
)

# Sign the hint
signed_hint = aihint.sign_hint(hint, "private_key.pem")

# Save to file
aihint.save_hint(signed_hint, "aihint.json")

# Validate and verify
print(aihint.validate_hint(signed_hint))  # True
print(aihint.verify_hint(signed_hint))    # True
```

## File Location

AiHint files should be placed at:
```
https://example.com/.well-known/aihint.json
```

## Documentation

- **[Implementation Guide](docs/user-guide/implementation-guide.md)** - Step-by-step integration guide
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Security Considerations](docs/technical/security-considerations.md)** - Security best practices
- **[Signature Algorithm](docs/SIGNATURES.md)** - Technical details on signing
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Security Policy](docs/contributing/security.md)** - Vulnerability reporting

## Structure

- `specs/` – Specifications of the AiHint format
- `schema/` – JSON Schema for validation
- `examples/` – Sample valid AiHint files
- `aihint/` – Python implementation library
- `tests/` – Test suite
- `tools/` – Command-line tools
- `docs/` – Documentation

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/

# Run with coverage
pytest --cov=aihint tests/
```

### Running Examples

```bash
# Create example AiHint with generated keys
python examples/create_hint.py
```

### Building Documentation

```bash
# Install development dependencies
pip install -r requirements.txt

# Run linting
flake8 aihint/

# Run type checking
mypy aihint/
```

## CLI Commands

### `aihint create`
Create a new AiHint metadata file.

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
- `--version` - AiHint version (default: 0.1)

### `aihint validate`
Validate an AiHint metadata file.

### `aihint verify`
Verify an AiHint metadata file signature.

### `aihint info`
Display information about an AiHint metadata file.

### `aihint sign`
Sign an existing AiHint metadata file.

## Security Considerations

- **Private Keys**: Keep your private keys secure and never share them
- **Key Rotation**: Regularly rotate your signing keys
- **Expiration**: Set appropriate expiration dates for your hints
- **HTTPS**: Always serve AiHint files over HTTPS
- **Validation**: Always validate hints before using them

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing/contributing.md) and [Code of Conduct](docs/contributing/code-of-conduct.md).

## License

MIT
