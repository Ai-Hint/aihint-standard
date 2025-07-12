# Python API Reference

The Python implementation of AiHint Standard provides a comprehensive library for creating, signing, and verifying AiHint metadata.

**Other implementations**: [JavaScript](javascript-api.md) | [PHP](php-api.md)

## Installation

```bash
pip install aihint
```

## Quick Start

```python
from aihint import AiHint

# Create and sign AiHint metadata
aihint = AiHint(
    target="https://example.com",
    issuer="https://example.com",
    score=0.85,
    method="aihint-core-v1"
)

aihint.sign("private_key.pem")
aihint.save("aihint.json")
```

## Core Classes

### AiHint

The main class for creating and managing AiHint metadata.

#### Constructor

```python
AiHint(
    target: str,
    issuer: str,
    score: float,
    method: str = "aihint-core-v1",
    comment: str = None,
    expires_at: datetime = None
)
```

**Parameters**:
- `target` (str): The target URL for this AiHint
- `issuer` (str): The issuer URL
- `score` (float): Trust score between 0.0 and 1.0
- `method` (str): Scoring method identifier
- `comment` (str, optional): Additional comment
- `expires_at` (datetime, optional): Expiration date

#### Methods

##### `sign(private_key_path: str) -> None`
Sign the AiHint metadata with a private key.

##### `verify(public_key_path: str = None) -> bool`
Verify the signature of the AiHint metadata.

##### `save(file_path: str) -> None`
Save the AiHint metadata to a JSON file.

##### `load(file_path: str) -> None`
Load AiHint metadata from a JSON file.

##### `validate() -> bool`
Validate the AiHint metadata structure.

## Key Management

### KeyManager

Utility class for generating and managing cryptographic keys.

```python
from aihint import KeyManager

# Generate a new key pair
key_manager = KeyManager()
key_manager.generate_keys("keys/")

# Load existing keys
private_key = key_manager.load_private_key("keys/private_key.pem")
public_key = key_manager.load_public_key("keys/public_key.pem")
```

## CLI Usage

The Python implementation includes a command-line interface:

```bash
# Generate keys
aihint generate-keys --output-dir ./keys

# Create and sign AiHint
aihint create \
  --target "https://example.com" \
  --issuer "https://example.com" \
  --score 0.85 \
  --private-key "keys/private_key.pem" \
  --output "aihint.json"

# Verify AiHint
aihint verify aihint.json

# Validate AiHint
aihint validate aihint.json
```

## Examples

### Basic Usage

```python
from aihint import AiHint
from datetime import datetime, timezone, timedelta

# Create AiHint with expiration
expires_at = datetime.now(timezone.utc) + timedelta(days=365)
aihint = AiHint(
    target="https://mywebsite.com",
    issuer="https://mywebsite.com",
    score=0.92,
    method="aihint-core-v1",
    comment="My website trust metadata",
    expires_at=expires_at
)

# Sign and save
aihint.sign("private_key.pem")
aihint.save("aihint.json")
```

### Verification

```python
from aihint import AiHint

# Load and verify
aihint = AiHint()
aihint.load("aihint.json")

if aihint.verify("public_key.pem"):
    print("Signature is valid!")
    print(f"Trust score: {aihint.score}")
else:
    print("Signature verification failed!")
```

### Batch Processing

```python
import os
from aihint import AiHint

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            aihint = AiHint()
            aihint.load(filepath)
            
            if aihint.validate():
                print(f"{filename}: Valid")
            else:
                print(f"{filename}: Invalid")
```

## Error Handling

```python
from aihint import AiHintError

try:
    aihint = AiHint()
    aihint.load("aihint.json")
    aihint.verify("public_key.pem")
except AiHintError as e:
    print(f"AiHint error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

The Python implementation supports configuration through environment variables:

- `AIHINT_DEFAULT_METHOD`: Default scoring method
- `AIHINT_DEFAULT_EXPIRY_DAYS`: Default expiration period in days
- `AIHINT_KEY_DIRECTORY`: Default directory for key files

## See Also

- [JavaScript API](javascript-api.md) - Node.js implementation
- [PHP API](php-api.md) - PHP implementation
- [CLI Reference](cli-reference.md) - Command-line interface
- [Implementation Guide](../user-guide/implementation-guide.md) - Detailed usage guide 