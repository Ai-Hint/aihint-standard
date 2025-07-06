# AIHint FAQ

**Q: What is AIHint?**
A: An open standard for signed, verifiable website metadata for AI systems.

**Q: Where should I host my AIHint file?**
A: At `https://yourdomain.com/.well-known/aihint.json`.

**Q: How do I generate keys?**
A: Use OpenSSL or the provided example script. See the Implementation Guide.

**Q: What if my private key is compromised?**
A: Revoke the key, generate a new one, and update your AIHint file and public key URL.

**Q: Can I use algorithms other than RSA?**
A: Not in v0.1. Future versions may support more.

**Q: How do I validate or verify a hint?**
A: Use the CLI: `aihint validate` and `aihint verify`.

**Q: What is the trust score?**
A: A value (0.0–1.0) representing the issuer's assessment of the domain's trustworthiness.

**Q: Can I issue my own hints?**
A: Yes, but trust depends on your reputation as an issuer. 