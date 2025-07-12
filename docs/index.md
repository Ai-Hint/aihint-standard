# AiHint Standard

An open standard for signed, verifiable metadata for websites.

## What is AiHint?

AiHint Standard provides a way to add signed, verifiable metadata to websites. This metadata can include information about the site's purpose, ownership, security practices, and more. The signatures ensure that the metadata hasn't been tampered with and comes from a trusted source.

## Quick Navigation

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

## Supported Languages

AiHint Standard is implemented in multiple programming languages to make it easy to integrate into your existing projects:

| Language | Status | Features |
|----------|--------|----------|
| **Python** | ✅ Production Ready | Core library, CLI, key generation |
| **JavaScript/Node.js** | ✅ Production Ready | Core library, CLI, TypeScript support |
| **PHP** | ✅ Production Ready | Core library, CLI, key generation, remote key fetching |

## Key Features

- **Multi-language Support**: Choose from Python, JavaScript, or PHP
- **Self-signing**: Create and sign your own metadata for development/testing
- **Trusted Issuers**: Use official AiHint Issuer service for production
- **CLI Tools**: Command-line interfaces for all implementations
- **Key Management**: Generate and manage cryptographic keys
- **Validation**: Verify metadata integrity and authenticity

## Getting Started

1. **[Choose your implementation](getting-started/choose-implementation.md)** - Select Python, JavaScript, or PHP
2. **[Quick Start](getting-started/quick-start.md)** - Get up and running in minutes
3. **[Key Concepts](getting-started/key-concepts.md)** - Understand the fundamentals

## Open Source vs Production

<div class="admonition warning" markdown>
**Important**: This repository contains the **open source protocol** for AiHint Standard, which is designed for development, testing, and self-signing. For production use with global trust, you'll need to use the official **AiHint Issuer service**.
</div>

- **Open Source** (this repo): Free, self-signing, development/testing
- **AiHint Issuer Service**: Production-ready, globally trusted, paid service

## Contributing

We welcome contributions! See our [Contributing Guide](contributing/contributing.md) for details.

## License

This project is licensed under the MIT License. 