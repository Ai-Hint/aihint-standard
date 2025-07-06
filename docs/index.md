# AIHint Standard Documentation

Welcome to the AIHint Standard documentation! AIHint is an open standard for exposing signed, verifiable metadata for websites, intended to be read by AI systems, LLMs, and intelligent agents.

## What is AIHint?

AIHint allows any AI system to:
- Discover a well-known, machine-readable JSON file on a website
- Verify its cryptographic signature
- Understand the site's declared trust score and metadata

## Quick Start

```bash
# Install AIHint
pip install aihint

# Create your first AIHint
aihint create \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --score 0.92 \
  --method "aihint-core-v1" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --private-key "private_key.pem" \
  --output "aihint.json"
```

## Key Features

- **Cryptographic Signatures**: RSA 2048-bit with SHA-256
- **Trust Scoring**: 0.0-1.0 scale with customizable methods
- **Expiration**: Built-in expiration dates for security
- **Validation**: Comprehensive schema and signature validation
- **CLI Tools**: Easy-to-use command-line interface
- **Python API**: Full programmatic access

## Documentation Sections

- **[Getting Started](getting-started/quick-start.md)** - Quick start guide and installation
- **[User Guide](user-guide/implementation-guide.md)** - Implementation guide and API reference
- **[Technical Reference](technical/security-considerations.md)** - Security considerations and technical details
- **[Contributing](contributing/contributing.md)** - How to contribute to the project

## File Location

AIHint files should be placed at:
```
https://example.com/.well-known/aihint.json
```

## Example AIHint File

```json
{
  "version": "0.1",
  "type": "global",
  "target": "https://example.com",
  "issuer": "https://trust.aihint.org",
  "score": 0.92,
  "method": "aihint-core-v1",
  "issued_at": "2025-01-01T12:00:00Z",
  "expires_at": "2026-01-01T00:00:00Z",
  "comment": "Example AIHint for demonstration",
  "signature": "base64-signature-here",
  "public_key_url": "https://trust.aihint.org/pubkey.pem"
}
```

## Security

AIHint is designed with security in mind. See our [Security Considerations](technical/security-considerations.md) for best practices and potential attack vectors.

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing/contributing.md) and [Code of Conduct](contributing/code-of-conduct.md). 