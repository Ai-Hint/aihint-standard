"""
AIHint Data Models

Pydantic models for AIHint data structures with validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class AIHintGlobal(BaseModel):
    """AIHint Global metadata model."""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    version: str = Field(..., description="AIHint version")
    type: str = Field("global", description="Hint type")
    target: str = Field(..., description="Target domain URL")
    issuer: str = Field(..., description="URL of the issuing authority")
    score: float = Field(..., ge=0.0, le=1.0, description="Trust/reputation score")
    method: str = Field(..., description="Scoring method used")
    issued_at: datetime = Field(..., description="ISO 8601 timestamp")
    expires_at: datetime = Field(..., description="ISO 8601 expiration timestamp")
    comment: Optional[str] = Field(None, description="Optional human-readable comment")
    signature: str = Field(..., description="Base64 signature")
    public_key_url: str = Field(..., description="URL to fetch the issuer's public key")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v != "global":
            raise ValueError("Type must be 'global'")
        return v
    
    @field_validator('target', 'issuer', 'public_key_url')
    @classmethod
    def validate_urls(cls, v):
        if not re.match(r'^https?://', v):
            raise ValueError("Must be a valid HTTP/HTTPS URL")
        return v
    
    @field_validator('issued_at', 'expires_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class AIHintData(BaseModel):
    """Base AIHint data model."""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    version: str
    type: str
    target: str
    issuer: str
    issued_at: datetime
    expires_at: datetime
    signature: str
    public_key_url: str
    comment: Optional[str] = None 