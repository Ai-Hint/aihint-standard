# AIHint Signature Algorithm

## Algorithm
- **Type:** RSA
- **Key Size:** 2048 bits (minimum)
- **Hash:** SHA-256
- **Padding:** PKCS#1 v1.5
- **Encoding:** Base64

## Signing Process
1. Remove the `signature` field from the JSON object.
2. Sort all keys alphabetically.
3. Serialize to canonical JSON (no whitespace, sorted keys).
4. Sign the resulting bytes with the issuer's private RSA key.
5. Encode the signature in Base64 and insert as the `signature` field.

## Verification Process
1. Remove the `signature` field from the JSON object.
2. Sort all keys alphabetically.
3. Serialize to canonical JSON (no whitespace, sorted keys).
4. Fetch the issuer's public key from `public_key_url`.
5. Verify the signature using RSA/SHA-256.

## Example
See `examples/create_hint.py` for a full signing workflow. 