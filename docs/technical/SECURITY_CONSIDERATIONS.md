# AIHint Security Considerations

AIHint is designed to provide verifiable, tamper-evident metadata for websites. Security is critical to its trustworthiness.

## Signature Algorithms
- **Default:** RSA 2048-bit with SHA-256
- **Padding:** PKCS#1 v1.5
- **Encoding:** Base64

## Key Management
- Keep private keys secure and offline when possible
- Rotate keys regularly
- Use strong, unique passphrases for key storage

## Attack Vectors
- **Key compromise:** If a private key is leaked, all issued hints can be forged
- **Replay attacks:** Use `issued_at` and `expires_at` to limit hint validity
- **Man-in-the-middle:** Always fetch public keys and aihint.json over HTTPS
- **Signature algorithm downgrade:** Only accept strong, documented algorithms

## Recommendations
- Validate all fields and signatures before trusting a hint
- Monitor for revoked or expired keys
- Use trusted authorities for `issuer` and `public_key_url`
- Consider using certificate transparency or public key pinning for issuers 