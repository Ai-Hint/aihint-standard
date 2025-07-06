"""
Tests for AIHint core functionality.
"""

import json
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from aihint.core import AIHint, AIHintValidator, AIHintSigner, AIHintVerifier, AIHintError
from aihint.models import AIHintGlobal


class TestAIHintValidator:
    """Test AIHint validation functionality."""
    
    def test_valid_data(self):
        """Test validation of valid AIHint data."""
        validator = AIHintValidator()
        
        valid_data = {
            "version": "0.1",
            "type": "global",
            "target": "https://example.com",
            "issuer": "https://trust.aihint.org",
            "score": 0.92,
            "method": "aihint-core-v1",
            "issued_at": "2025-01-01T12:00:00Z",
            "expires_at": "2026-01-01T00:00:00Z",
            "signature": "base64-signature",
            "public_key_url": "https://trust.aihint.org/pubkey.pem"
        }
        
        assert validator.validate(valid_data) is True
    
    def test_invalid_data(self):
        """Test validation of invalid AIHint data."""
        validator = AIHintValidator()
        
        invalid_data = {
            "version": "0.1",
            "type": "invalid",  # Invalid type
            "target": "not-a-url",  # Invalid URL
            "score": 1.5,  # Score out of range
        }
        
        with pytest.raises(Exception):
            validator.validate(invalid_data)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        validator = AIHintValidator()
        
        incomplete_data = {
            "version": "0.1",
            "type": "global",
            # Missing required fields
        }
        
        with pytest.raises(Exception):
            validator.validate(incomplete_data)


class TestAIHintSigner:
    """Test AIHint signing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Generate test key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Create temporary key files
        self.private_key_file = tempfile.NamedTemporaryFile(delete=False)
        self.public_key_file = tempfile.NamedTemporaryFile(delete=False)
        
        # Write keys to files
        self.private_key_file.write(
            self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
        self.private_key_file.close()
        
        self.public_key_file.write(
            self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
        self.public_key_file.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        os.unlink(self.private_key_file.name)
        os.unlink(self.public_key_file.name)
    
    def test_sign_data(self):
        """Test signing AIHint data."""
        signer = AIHintSigner(self.private_key_file.name)
        
        data = {
            "version": "0.1",
            "type": "global",
            "target": "https://example.com",
            "issuer": "https://trust.aihint.org",
            "score": 0.92,
            "method": "aihint-core-v1",
            "issued_at": "2025-01-01T12:00:00Z",
            "expires_at": "2026-01-01T00:00:00Z",
            "public_key_url": "https://trust.aihint.org/pubkey.pem"
        }
        
        signature = signer.sign(data)
        assert signature is not None
        assert len(signature) > 0
    
    def test_signature_deterministic(self):
        """Test that signatures are deterministic."""
        signer = AIHintSigner(self.private_key_file.name)
        
        data = {
            "version": "0.1",
            "type": "global",
            "target": "https://example.com",
            "issuer": "https://trust.aihint.org",
            "score": 0.92,
            "method": "aihint-core-v1",
            "issued_at": "2025-01-01T12:00:00Z",
            "expires_at": "2026-01-01T00:00:00Z",
            "public_key_url": "https://trust.aihint.org/pubkey.pem"
        }
        
        signature1 = signer.sign(data)
        signature2 = signer.sign(data)
        
        assert signature1 == signature2


class TestAIHintVerifier:
    """Test AIHint verification functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Generate test key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Create temporary key files
        self.private_key_file = tempfile.NamedTemporaryFile(delete=False)
        self.public_key_file = tempfile.NamedTemporaryFile(delete=False)
        
        # Write keys to files
        self.private_key_file.write(
            self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
        self.private_key_file.close()
        
        self.public_key_file.write(
            self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
        self.public_key_file.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        os.unlink(self.private_key_file.name)
        os.unlink(self.public_key_file.name)
    
    @patch('requests.Session.get')
    def test_verify_signature(self, mock_get):
        """Test signature verification."""
        # Mock the public key fetch
        with open(self.public_key_file.name, 'rb') as f:
            mock_response = MagicMock()
            mock_response.content = f.read()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
        
        verifier = AIHintVerifier()
        
        # Create and sign data
        signer = AIHintSigner(self.private_key_file.name)
        
        data = {
            "version": "0.1",
            "type": "global",
            "target": "https://example.com",
            "issuer": "https://trust.aihint.org",
            "score": 0.92,
            "method": "aihint-core-v1",
            "issued_at": "2025-01-01T12:00:00Z",
            "expires_at": "2026-01-01T00:00:00Z",
            "public_key_url": "https://trust.aihint.org/pubkey.pem"
        }
        
        signature = signer.sign(data)
        data["signature"] = signature
        
        # Verify signature
        assert verifier.verify(data) is True
    
    @patch('requests.Session.get')
    def test_verify_invalid_signature(self, mock_get):
        """Test verification of invalid signature."""
        # Mock the public key fetch
        with open(self.public_key_file.name, 'rb') as f:
            mock_response = MagicMock()
            mock_response.content = f.read()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
        
        verifier = AIHintVerifier()
        
        data = {
            "version": "0.1",
            "type": "global",
            "target": "https://example.com",
            "issuer": "https://trust.aihint.org",
            "score": 0.92,
            "method": "aihint-core-v1",
            "issued_at": "2025-01-01T12:00:00Z",
            "expires_at": "2026-01-01T00:00:00Z",
            "signature": "invalid-signature",
            "public_key_url": "https://trust.aihint.org/pubkey.pem"
        }
        
        with pytest.raises(Exception):
            verifier.verify(data)


class TestAIHint:
    """Test main AIHint class."""
    
    def test_create_global_hint(self):
        """Test creating a global hint."""
        aihint = AIHint()
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=365)
        
        hint = aihint.create_global_hint(
            target="https://example.com",
            issuer="https://trust.aihint.org",
            score=0.92,
            method="aihint-core-v1",
            public_key_url="https://trust.aihint.org/pubkey.pem",
            expires_at=expires_at,
            comment="Test hint"
        )
        
        assert isinstance(hint, AIHintGlobal)
        assert hint.target == "https://example.com"
        assert hint.score == 0.92
        assert hint.type == "global"
    
    def test_save_and_load_hint(self):
        """Test saving and loading hints."""
        aihint = AIHint()
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=365)
        
        hint = aihint.create_global_hint(
            target="https://example.com",
            issuer="https://trust.aihint.org",
            score=0.92,
            method="aihint-core-v1",
            public_key_url="https://trust.aihint.org/pubkey.pem",
            expires_at=expires_at
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            aihint.save_hint(hint, temp_file)
            
            # Load from file
            loaded_hint = aihint.load_hint(temp_file)
            
            assert loaded_hint.target == hint.target
            assert loaded_hint.score == hint.score
            assert loaded_hint.type == hint.type
            
        finally:
            os.unlink(temp_file)
    
    def test_validate_hint(self):
        """Test hint validation."""
        aihint = AIHint()
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=365)
        
        hint = aihint.create_global_hint(
            target="https://example.com",
            issuer="https://trust.aihint.org",
            score=0.92,
            method="aihint-core-v1",
            public_key_url="https://trust.aihint.org/pubkey.pem",
            expires_at=expires_at,
            comment="Test comment"
        )
        
        assert aihint.validate_hint(hint) is True 