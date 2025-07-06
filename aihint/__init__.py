"""
AIHint Standard Implementation

A Python library for creating, validating, and verifying AIHint metadata files.
"""

__version__ = "0.1.0"
__author__ = "AIHint Contributors"

from .core import AIHint, AIHintValidator, AIHintSigner, AIHintVerifier
from .models import AIHintData, AIHintGlobal

__all__ = [
    "AIHint",
    "AIHintValidator", 
    "AIHintSigner",
    "AIHintVerifier",
    "AIHintData",
    "AIHintGlobal"
] 