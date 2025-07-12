# AiHint Implementation Guide

This guide walks you through integrating AiHint into your website or service.

## 1. Generate Key Pair

```
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

## 2. Create AiHint Metadata

Use the CLI or Python API:

```
aihint create \
  --target "https://yourdomain.com" \
  --issuer "https://your-issuer.com" \
  --score 0.95 \
  --method "aihint-core-v1" \
  --public-key-url "https://your-issuer.com/pubkey.pem" \
  --private-key private_key.pem \
  --output .well-known/aihint.json
```

## 3. Publish Files
- Place `aihint.json` at `https://yourdomain.com/.well-known/aihint.json`
- Host your public key at the `public_key_url`

## 4. Verification
- Use the CLI or Python API to verify your hint:
```
aihint verify .well-known/aihint.json
```

## 5. Rotate Keys (Recommended)
- Generate new keys periodically
- Update `public_key_url` and re-sign your hints

## 6. Example
See `examples/create_hint.py` for a full workflow. 