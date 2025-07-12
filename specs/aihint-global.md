# AiHint Global — Specification v0.1

The Global Hint is a JSON file placed at `.well-known/aihint.json`, allowing AI systems to obtain trusted metadata about a domain.

## Location

```
https://example.com/.well-known/aihint.json
```

## Fields

| Field            | Type    | Description |
|------------------|---------|-------------|
| `version`        | string  | AiHint version (e.g., `"0.1"`) |
| `type`           | string  | `"global"` |
| `target`         | string  | Target domain URL |
| `issuer`         | string  | URL of the issuing authority |
| `score`          | float   | Trust/reputation score (0.0 - 1.0) |
| `method`         | string  | Scoring method used |
| `issued_at`      | string  | ISO 8601 timestamp |
| `expires_at`     | string  | ISO 8601 expiration timestamp |
| `comment`        | string  | Optional human-readable comment |
| `signature`      | string  | Base64 signature (excluding itself) |
| `public_key_url` | string  | URL to fetch the issuer’s public key |
