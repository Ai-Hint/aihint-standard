#!/usr/bin/env python3
"""
Example: Create and sign an AIHint metadata file.

This script demonstrates how to create a signed AIHint metadata file
for a website using the AIHint library.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Add the parent directory to the path so we can import aihint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aihint import AIHint


def generate_key_pair(private_key_path: str, public_key_path: str):
    """Generate a new RSA key pair for testing."""
    print("Generating RSA key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Save private key
    with open(private_key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save public key
    public_key = private_key.public_key()
    with open(public_key_path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    print(f"✓ Keys generated:")
    print(f"  Private key: {private_key_path}")
    print(f"  Public key: {public_key_path}")


def create_example_hint():
    """Create an example AIHint metadata file."""
    print("\nCreating AIHint metadata...")
    
    # Initialize AIHint
    aihint = AIHint()
    
    # Set expiration to 1 year from now
    expires_at = datetime.now(timezone.utc) + timedelta(days=365)
    
    # Create the hint
    hint = aihint.create_global_hint(
        target="https://example.com",
        issuer="https://trust.aihint.org",
        score=0.92,
        method="aihint-core-v1",
        public_key_url="https://trust.aihint.org/pubkey.pem",
        expires_at=expires_at,
        comment="Example AIHint for demonstration purposes"
    )
    
    print("✓ AIHint created successfully")
    return hint


def sign_hint(hint, private_key_path: str):
    """Sign the AIHint with a private key."""
    print(f"\nSigning AIHint with private key: {private_key_path}")
    
    aihint = AIHint()
    signed_hint = aihint.sign_hint(hint, private_key_path)
    
    print("✓ AIHint signed successfully")
    return signed_hint


def save_hint(hint, output_path: str):
    """Save the AIHint to a JSON file."""
    print(f"\nSaving AIHint to: {output_path}")
    
    aihint = AIHint()
    aihint.save_hint(hint, output_path)
    
    print("✓ AIHint saved successfully")


def validate_hint(hint):
    """Validate the AIHint."""
    print("\nValidating AIHint...")
    
    aihint = AIHint()
    
    if aihint.validate_hint(hint):
        print("✓ AIHint validation passed")
    else:
        print("✗ AIHint validation failed")
        return False
    
    # Check expiration
    now = datetime.now(timezone.utc)
    if hint.expires_at < now:
        print("⚠ Warning: AIHint has expired")
    else:
        days_left = (hint.expires_at - now).days
        print(f"✓ AIHint valid for {days_left} more days")
    
    return True


def main():
    """Main function to create a complete AIHint example."""
    print("AIHint Example: Create and Sign Metadata")
    print("=" * 50)
    
    # File paths
    private_key_path = "example_private_key.pem"
    public_key_path = "example_public_key.pem"
    output_path = "example_aihint.json"
    
    try:
        # Generate key pair if it doesn't exist
        if not os.path.exists(private_key_path):
            generate_key_pair(private_key_path, public_key_path)
        
        # Create hint
        hint = create_example_hint()
        
        # Validate before signing
        if not validate_hint(hint):
            print("✗ Validation failed, aborting")
            return
        
        # Sign the hint
        signed_hint = sign_hint(hint, private_key_path)
        
        # Save to file
        save_hint(signed_hint, output_path)
        
        # Final validation
        print("\n" + "=" * 50)
        print("Final validation:")
        validate_hint(signed_hint)
        
        print(f"\n✓ Complete! AIHint saved to: {output_path}")
        print("\nTo use this AIHint file:")
        print(f"1. Place {output_path} at https://example.com/.well-known/aihint.json")
        print(f"2. Host the public key at https://trust.aihint.org/pubkey.pem")
        print("3. AI systems can now discover and verify your trust metadata")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 