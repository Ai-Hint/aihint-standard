---
title: AiHint Standard - Open Standard for Signed Website Metadata
description: Create trusted, cryptographically signed metadata for websites with multi-language support (Python, JavaScript, PHP). CLI tools, key management, and comprehensive documentation.
keywords: 
  - aihint
  - website metadata
  - signed metadata
  - cryptographic signatures
  - trust verification
  - python
  - javascript
  - php
  - cli tools
  - key management
  - open standard
  - security
  - verification
  - digital signatures
  - rsa
  - sha256
authors:
  - name: AiHint Contributors
    url: https://github.com/Ai-Hint/aihint-standard
---

# AiHint Standard

**Open standard for signed, verifiable website metadata with multi-language support**

<div class="grid" markdown>

### 🚀 Get Started
[Choose Your Implementation →](getting-started/choose-implementation.md)

### 📚 Documentation
- [User Guide](user-guide/implementation-guide.md)
- [API Reference](api-reference/python-api.md)
- [Technical Details](technical/protocol.md)

### 🔧 Implementations
- [Python](api-reference/python-api.md)
- [JavaScript/Node.js](api-reference/javascript-api.md)
- [PHP](api-reference/php-api.md)

</div>

## What is AiHint Standard?

AiHint Standard is an **open protocol** for creating cryptographically signed, verifiable metadata for websites. This metadata can include information about a site's purpose, ownership, security practices, trust scores, and more. The **RSA-2048 signatures with SHA-256** ensure that the metadata hasn't been tampered with and comes from a trusted source.

### Key Benefits

- ✅ **Cryptographic Security**: RSA-2048 signatures with SHA-256 hashing
- ✅ **Multi-Language Support**: Python, JavaScript, PHP implementations
- ✅ **CLI Tools**: Command-line interfaces for all languages
- ✅ **Key Management**: Generate and manage cryptographic keys
- ✅ **Validation**: Verify metadata integrity and authenticity
- ✅ **Open Standard**: Free to use, open source protocol

## Supported Languages & Features

| Language | Status | Features | Package |
|----------|--------|----------|---------|
| **Python** | ✅ Production Ready | Core library, CLI, key generation, validation | `pip install aihint-standard` |
| **JavaScript/Node.js** | ✅ Production Ready | Core library, CLI, TypeScript support, validation | `npm install aihint-standard` |
| **PHP** | ✅ Production Ready | Core library, CLI, key generation, remote fetching | `composer require aihint-standard/aihint` |

## Quick Start Examples

### Python
```python
from aihint import create_hint, verify_hint

# Create and sign metadata
hint = create_hint(
    target="https://example.com",
    issuer="https://trust.aihint.org", 
    score=0.85,
    private_key=private_key_pem
)

# Verify signature
is_valid = verify_hint(hint, public_key_pem)
```

### JavaScript
```javascript
const { createHint, verifyHint } = require('aihint-standard');

// Create and sign metadata
const hint = createHint({
    target: 'https://example.com',
    issuer: 'https://trust.aihint.org',
    score: 0.85
}, privateKeyPem);

// Verify signature
const isValid = verifyHint(hint, publicKeyPem);
```

### PHP
```php
use AiHintStandard\AiHint;

// Create and sign metadata
$hint = AiHint::createAndSign(
    'https://example.com',
    'https://trust.aihint.org',
    0.85,
    $privateKeyPem
);

// Verify signature
$isValid = $hint->verify($publicKeyPem);
```

## Use Cases

### 🔒 **Security & Trust**
- Verify website authenticity and ownership
- Establish trust scores for websites
- Prevent phishing and spoofing attacks
- Cryptographic proof of metadata integrity

### 🏢 **Enterprise & Compliance**
- Corporate website verification
- Compliance documentation
- Audit trails for website metadata
- Brand protection and verification

### 🌐 **Web Standards**
- Open standard for website metadata
- Interoperable across platforms
- Extensible for future use cases
- Community-driven development

### 🛠 **Developer Tools**
- CLI tools for automation
- Multi-language SDKs
- Comprehensive documentation
- Open source implementation

## Getting Started

1. **[Choose your implementation](getting-started/choose-implementation.md)** - Select Python, JavaScript, or PHP
2. **[Quick Start](getting-started/quick-start.md)** - Get up and running in minutes
3. **[Key Concepts](getting-started/key-concepts.md)** - Understand the fundamentals
4. **[API Reference](api-reference/python-api.md)** - Detailed documentation

## Open Source vs Production

<div class="admonition warning" markdown>
**Important**: This repository contains the **open source protocol** for AiHint Standard, which is designed for development, testing, and self-signing. For production use with global trust, you'll need to use the official **AiHint Issuer service**.
</div>

| Feature | Open Source | AiHint Issuer Service |
|---------|-------------|----------------------|
| **Cost** | Free | Paid service |
| **Trust Level** | Self-signed | Globally trusted |
| **Use Case** | Development, testing | Production, public |
| **Validation** | Local verification | Global verification |
| **Support** | Community | Official support |

## Technical Specifications

- **Signature Algorithm**: RSA-2048 with SHA-256
- **Key Format**: PEM-encoded PKCS#8 private keys
- **Data Format**: JSON with snake_case keys
- **Version**: 0.1 (current protocol version)
- **Encoding**: UTF-8 JSON with Base64 signatures

## Community & Support

- 📖 **[Documentation](getting-started/quick-start.md)** - Comprehensive guides
- 🐛 **[Issues](https://github.com/Ai-Hint/aihint-standard/issues)** - Report bugs
- 💬 **[Discussions](https://github.com/Ai-Hint/aihint-standard/discussions)** - Ask questions
- 🤝 **[Contributing](contributing/contributing.md)** - Help improve the project
- 📄 **[Code of Conduct](contributing/code-of-conduct.md)** - Community guidelines

## License

This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/Ai-Hint/aihint-standard/blob/main/LICENSE) file for details.

---

<div class="admonition info" markdown>
**Ready to get started?** Check out our [implementation guide](user-guide/implementation-guide.md) or jump straight to [quick start](getting-started/quick-start.md).
</div> 