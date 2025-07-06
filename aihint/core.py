"""
AIHint Core Implementation

Core functionality for creating, validating, and verifying AIHint metadata.
"""

import json
import base64
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, cast
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import requests
from jsonschema import validate, ValidationError
from .models import AIHintGlobal, AIHintData


class AIHintError(Exception):
    """Base exception for AIHint operations."""
    pass


class AIHintValidationError(AIHintError):
    """Exception raised when AIHint validation fails."""
    pass


class AIHintSignatureError(AIHintError):
    """Exception raised when signature verification fails."""
    pass


class AIHintValidator:
    """Validates AIHint JSON data against the schema."""
    
    def __init__(self):
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for validation."""
        schema_path = "schema/aihint-global.schema.json"
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to embedded schema if file not found
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["version", "type", "target", "issuer", "score", "method", 
                           "issued_at", "expires_at", "signature", "public_key_url"],
                "properties": {
                    "version": {"type": "string"},
                    "type": {"type": "string", "enum": ["global"]},
                    "target": {"type": "string", "format": "uri"},
                    "issuer": {"type": "string", "format": "uri"},
                    "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "method": {"type": "string"},
                    "issued_at": {"type": "string", "format": "date-time"},
                    "expires_at": {"type": "string", "format": "date-time"},
                    "comment": {"type": ["string", "null"]},
                    "signature": {"type": "string"},
                    "public_key_url": {"type": "string", "format": "uri"}
                }
            }
    
    def _serialize_datetime(self, obj):
        """Convert datetime objects to ISO format strings."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def _prepare_data_for_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for validation by converting datetime objects."""
        if isinstance(data, dict):
            return {k: self._prepare_data_for_validation(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_data_for_validation(item) for item in data]
        else:
            return self._serialize_datetime(data)
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate AIHint data against the schema."""
        try:
            # Prepare data for validation
            validation_data = self._prepare_data_for_validation(data)
            validate(instance=validation_data, schema=self.schema)
            return True
        except ValidationError as e:
            raise AIHintValidationError(f"Schema validation failed: {e.message}")
    
    def validate_file(self, file_path: str) -> bool:
        """Validate an AIHint JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return self.validate(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise AIHintValidationError(f"File validation failed: {e}")


class AIHintSigner:
    """Signs AIHint data with cryptographic signatures."""
    
    def __init__(self, private_key_path: str):
        """Initialize with a private key file."""
        self.private_key = self._load_private_key(private_key_path)
    
    def _load_private_key(self, key_path: str) -> rsa.RSAPrivateKey:
        """Load private key from PEM file."""
        try:
            with open(key_path, 'rb') as f:
                key_data = f.read()
            key = load_pem_private_key(key_data, password=None)
            if not isinstance(key, rsa.RSAPrivateKey):
                raise AIHintError("Private key must be an RSA key")
            return key
        except Exception as e:
            raise AIHintError(f"Failed to load private key: {e}")
    
    def _create_signature_data(self, data: Dict[str, Any]) -> bytes:
        """Create the data to be signed (excluding the signature field)."""
        # Create a copy without the signature field
        sign_data = data.copy()
        sign_data.pop('signature', None)
        
        # Sort keys for deterministic signing
        sorted_data = dict(sorted(sign_data.items()))
        
        # Convert to canonical JSON
        json_str = json.dumps(sorted_data, separators=(',', ':'), sort_keys=True, default=str)
        return json_str.encode('utf-8')
    
    def sign(self, data: Dict[str, Any]) -> str:
        """Sign AIHint data and return base64 signature."""
        try:
            # Create data to sign
            sign_data = self._create_signature_data(data)
            
            # Create signature
            signature = self.private_key.sign(
                sign_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Return base64 encoded signature
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise AIHintError(f"Signing failed: {e}")


class AIHintVerifier:
    """Verifies AIHint signatures."""
    
    def __init__(self):
        self.session = requests.Session()
    
    def _fetch_public_key(self, public_key_url: str) -> rsa.RSAPublicKey:
        """Fetch public key from URL."""
        try:
            response = self.session.get(public_key_url, timeout=10)
            response.raise_for_status()
            key_data = response.content
            key = load_pem_public_key(key_data)
            if not isinstance(key, rsa.RSAPublicKey):
                raise AIHintError("Public key must be an RSA key")
            return key
        except Exception as e:
            raise AIHintError(f"Failed to fetch public key: {e}")
    
    def _create_signature_data(self, data: Dict[str, Any]) -> bytes:
        """Create the data that was signed (excluding the signature field)."""
        # Create a copy without the signature field
        sign_data = data.copy()
        sign_data.pop('signature', None)
        
        # Sort keys for deterministic verification
        sorted_data = dict(sorted(sign_data.items()))
        
        # Convert to canonical JSON
        json_str = json.dumps(sorted_data, separators=(',', ':'), sort_keys=True, default=str)
        return json_str.encode('utf-8')
    
    def verify(self, data: Dict[str, Any]) -> bool:
        """Verify AIHint signature."""
        try:
            # Extract signature and public key URL
            signature_b64 = data.get('signature')
            public_key_url = data.get('public_key_url')
            
            if not signature_b64 or not public_key_url:
                raise AIHintSignatureError("Missing signature or public_key_url")
            
            # Fetch public key
            public_key = self._fetch_public_key(public_key_url)
            
            # Create data that was signed
            sign_data = self._create_signature_data(data)
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            public_key.verify(
                signature,
                sign_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            return True
        except Exception as e:
            raise AIHintSignatureError(f"Signature verification failed: {e}")
    
    def verify_file(self, file_path: str) -> bool:
        """Verify an AIHint JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return self.verify(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise AIHintError(f"File verification failed: {e}")


class AIHint:
    """Main AIHint class for creating and managing AIHint metadata."""
    
    def __init__(self):
        self.validator = AIHintValidator()
        self.verifier = AIHintVerifier()
    
    def create_global_hint(
        self,
        target: str,
        issuer: str,
        score: float,
        method: str,
        public_key_url: str,
        expires_at: datetime,
        comment: Optional[str] = None,
        version: str = "0.1"
    ) -> AIHintGlobal:
        """Create a new AIHint Global metadata object."""
        now = datetime.now(timezone.utc)
        
        # Create base data
        data = {
            "version": version,
            "type": "global",
            "target": target,
            "issuer": issuer,
            "score": score,
            "method": method,
            "issued_at": now,
            "expires_at": expires_at,
            "public_key_url": public_key_url,
            "signature": "",  # Placeholder
            "comment": comment
        }
        
        # Create AIHintGlobal object
        hint = AIHintGlobal(**data)
        return hint
    
    def sign_hint(self, hint: AIHintGlobal, private_key_path: str) -> AIHintGlobal:
        """Sign an AIHint object."""
        signer = AIHintSigner(private_key_path)
        
        # Convert to dict for signing
        data = hint.model_dump()
        
        # Generate signature
        signature = signer.sign(data)
        
        # Update hint with signature
        hint.signature = signature
        return hint
    
    def validate_hint(self, hint: AIHintGlobal) -> bool:
        """Validate an AIHint object."""
        return self.validator.validate(hint.model_dump())
    
    def verify_hint(self, hint: AIHintGlobal) -> bool:
        """Verify an AIHint object's signature."""
        return self.verifier.verify(hint.model_dump())
    
    def save_hint(self, hint: AIHintGlobal, file_path: str) -> None:
        """Save AIHint object to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(hint.model_dump(), f, indent=2, default=str)
    
    def load_hint(self, file_path: str) -> AIHintGlobal:
        """Load AIHint object from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return AIHintGlobal(**data) 