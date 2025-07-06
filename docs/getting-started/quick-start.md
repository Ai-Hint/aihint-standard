# Quick Start Guide

Get up and running with AIHint in minutes!

## Installation

```bash
# Install from source
git clone https://github.com/aihint/aihint-standard.git
cd aihint-standard
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Create Your First AIHint

### Step 1: Generate Keys

```bash
# Generate RSA key pair
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

### Step 2: Create AIHint

```bash
# Create a signed AIHint metadata file
aihint create \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --score 0.92 \
  --method "aihint-core-v1" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --private-key "private_key.pem" \
  --output "aihint.json"
```

### Step 3: Validate and Verify

```bash
# Validate the AIHint file
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

## Next Steps

- Read the [Implementation Guide](../user-guide/implementation-guide.md) for detailed instructions
- Check out the [Security Considerations](../technical/security-considerations.md) for best practices
- Explore the [Python API](../user-guide/python-api.md) for advanced usage 