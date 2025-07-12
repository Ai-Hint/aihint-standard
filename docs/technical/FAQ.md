# AiHint FAQ

**Q: What is AiHint?**
A: AiHint is an open standard for signed, verifiable website metadata for AI systems and intelligent agents. It allows websites to publish cryptographically signed trust and metadata files that can be read and verified by AI, LLMs, and other consumers.

**Q: Who can issue AiHint metadata?**
A: Anyone can generate their own keys and self-sign AiHint metadata using the open source tools. However, self-signed metadata is not globally trusted by default. For production, public, or commercial use, you should use the official AiHint Issuer service, which provides domain validation, billing, and global trust.

**Q: What is the AiHint Official Issuer Service?**
A: The AiHint Official Issuer Service is a managed, closed-source platform that acts as the top-level trust authority for AiHint. It verifies issuers, manages billing, and issues globally trusted certificates for signing AiHint metadata. Only metadata signed by an official issuer is globally recognized and trusted by default.

**Q: How do I become an official AiHint issuer?**
A: You can apply through the AiHint Official Issuer Service. The process involves domain validation, registration, and (for some plans) billing. Once approved, you receive a certificate or key signed by AiHint, allowing you to issue globally trusted AiHint metadata.

**Q: Can I still use AiHint for free?**
A: Yes! The open source tools and protocol are free for experimentation, development, and self-hosted/private use. Only official issuer status (for global trust and production use) requires registration and may involve billing.

**Q: What happens if my issuer key is compromised?**
A: If you are an official issuer, you can revoke your certificate through the AiHint Issuer Service. Revocations are published in a public list. For self-signed keys, you should rotate your keys and update your metadata.

**Q: How does trust work in AiHint?**
A: Consumers (AIs, apps, etc.) trust metadata signed by official AiHint issuers by default. Self-signed metadata is only trusted if the consumer explicitly adds the issuer's key.

**Q: Where can I learn more or get support?**
A: See the [documentation](../index.md), join our community channels, or contact the AiHint team for more information. 