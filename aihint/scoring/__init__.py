"""
AiHint Trust Scoring System

A comprehensive trust scoring system that evaluates websites based on:
- Security metrics (SSL, headers, malware checks)
- Reputation signals (domain age, incidents, third-party data)
- Content & compliance (privacy policies, contact info, legal compliance)
"""

from .engine import TrustScoringEngine
from .metrics import SecurityMetrics, ReputationMetrics, ComplianceMetrics
from .scorers import (
    SSLTLSValidator,
    SecurityHeadersAnalyzer,
    MalwareChecker,
    DomainReputationChecker,
    DomainAgeAnalyzer,
    IncidentTracker,
    PrivacyPolicyAnalyzer,
    ContactValidator,
    ComplianceChecker
)

__all__ = [
    'TrustScoringEngine',
    'SecurityMetrics',
    'ReputationMetrics', 
    'ComplianceMetrics',
    'SSLTLSValidator',
    'SecurityHeadersAnalyzer',
    'MalwareChecker',
    'DomainReputationChecker',
    'DomainAgeAnalyzer',
    'IncidentTracker',
    'PrivacyPolicyAnalyzer',
    'ContactValidator',
    'ComplianceChecker'
]
