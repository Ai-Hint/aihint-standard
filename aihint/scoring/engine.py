"""
Trust Scoring Engine

Main engine that orchestrates all scoring metrics and produces final trust scores.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

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


class TrustLevel(Enum):
    """Trust level classifications based on score ranges."""
    VERY_LOW = (0.0, 0.29, "Very low trust (malicious, compromised, or highly suspicious)")
    LOW = (0.3, 0.49, "Low trust (multiple red flags, proceed with caution)")
    MODERATE = (0.5, 0.69, "Moderate trust (newer sites, some concerns)")
    GOOD = (0.7, 0.89, "Good trust (legitimate businesses, established sites)")
    HIGH = (0.9, 1.0, "Highly trusted (banks, major corporations, verified entities)")
    
    def __init__(self, min_score: float, max_score: float, description: str):
        self.min_score = min_score
        self.max_score = max_score
        self.description = description
    
    @classmethod
    def from_score(cls, score: float) -> 'TrustLevel':
        """Get trust level from score."""
        for level in cls:
            if level.min_score <= score <= level.max_score:
                return level
        return cls.VERY_LOW


@dataclass
class ScoringResult:
    """Result of trust scoring analysis."""
    url: str
    final_score: float
    trust_level: TrustLevel
    confidence: float
    security_score: float
    reputation_score: float
    compliance_score: float
    detailed_metrics: Dict[str, Any]
    warnings: List[str]
    errors: List[str]
    timestamp: datetime
    method: str = "aihint-scoring-v1"


class TrustScoringEngine:
    """
    Main trust scoring engine that combines all metrics to produce final scores.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scoring engine with configuration.
        
        Args:
            config: Configuration dictionary with API keys, timeouts, etc.
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize metric collectors
        self.security_metrics = SecurityMetrics()
        self.reputation_metrics = ReputationMetrics()
        self.compliance_metrics = ComplianceMetrics()
        
        # Initialize scorers
        self.scorers = {
            'ssl_tls': SSLTLSValidator(config.get('ssl', {})),
            'security_headers': SecurityHeadersAnalyzer(config.get('headers', {})),
            'malware': MalwareChecker(config.get('malware', {})),
            'domain_reputation': DomainReputationChecker(config.get('reputation', {})),
            'domain_age': DomainAgeAnalyzer(config.get('domain_age', {})),
            'incidents': IncidentTracker(config.get('incidents', {})),
            'privacy_policy': PrivacyPolicyAnalyzer(config.get('privacy', {})),
            'contact': ContactValidator(config.get('contact', {})),
            'compliance': ComplianceChecker(config.get('compliance', {}))
        }
        
        # Scoring weights (can be configured)
        self.weights = {
            'security': 0.4,      # 40% weight for security metrics
            'reputation': 0.35,   # 35% weight for reputation signals
            'compliance': 0.25    # 25% weight for compliance metrics
        }
    
    async def score_website(self, url: str) -> ScoringResult:
        """
        Score a website's trustworthiness.
        
        Args:
            url: The website URL to score
            
        Returns:
            ScoringResult with detailed analysis
        """
        self.logger.info(f"Starting trust scoring for {url}")
        
        warnings = []
        errors = []
        detailed_metrics = {}
        
        try:
            # Run all scoring tasks in parallel for efficiency
            scoring_tasks = [
                self._score_security_metrics(url),
                self._score_reputation_metrics(url),
                self._score_compliance_metrics(url)
            ]
            
            security_result, reputation_result, compliance_result = await asyncio.gather(
                *scoring_tasks, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(security_result, Exception):
                errors.append(f"Security scoring failed: {security_result}")
                security_result = {'score': 0.0, 'metrics': {}}
            
            if isinstance(reputation_result, Exception):
                errors.append(f"Reputation scoring failed: {reputation_result}")
                reputation_result = {'score': 0.0, 'metrics': {}}
            
            if isinstance(compliance_result, Exception):
                errors.append(f"Compliance scoring failed: {compliance_result}")
                compliance_result = {'score': 0.0, 'metrics': {}}
            
            # Calculate weighted final score
            final_score = self._calculate_weighted_score(
                security_result['score'],
                reputation_result['score'], 
                compliance_result['score']
            )
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(
                security_result['metrics'],
                reputation_result['metrics'],
                compliance_result['metrics']
            )
            
            # Compile detailed metrics
            detailed_metrics = {
                'security': security_result['metrics'],
                'reputation': reputation_result['metrics'],
                'compliance': compliance_result['metrics']
            }
            
            # Generate warnings based on low scores
            if security_result['score'] < 0.5:
                warnings.append("Low security score detected")
            if reputation_result['score'] < 0.5:
                warnings.append("Low reputation score detected")
            if compliance_result['score'] < 0.5:
                warnings.append("Low compliance score detected")
            
            trust_level = TrustLevel.from_score(final_score)
            
            result = ScoringResult(
                url=url,
                final_score=final_score,
                trust_level=trust_level,
                confidence=confidence,
                security_score=security_result['score'],
                reputation_score=reputation_result['score'],
                compliance_score=compliance_result['score'],
                detailed_metrics=detailed_metrics,
                warnings=warnings,
                errors=errors,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.logger.info(f"Scoring completed for {url}: {final_score:.3f} ({trust_level.name})")
            return result
            
        except Exception as e:
            self.logger.error(f"Scoring failed for {url}: {e}")
            return ScoringResult(
                url=url,
                final_score=0.0,
                trust_level=TrustLevel.VERY_LOW,
                confidence=0.0,
                security_score=0.0,
                reputation_score=0.0,
                compliance_score=0.0,
                detailed_metrics={},
                warnings=[],
                errors=[f"Scoring engine error: {e}"],
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _score_security_metrics(self, url: str) -> Dict[str, Any]:
        """Score security-related metrics."""
        metrics = {}
        total_score = 0.0
        max_score = 0.0
        
        # SSL/TLS validation
        ssl_score, ssl_metrics = await self.scorers['ssl_tls'].score(url)
        metrics['ssl_tls'] = ssl_metrics
        total_score += ssl_score * 0.4
        max_score += 0.4
        
        # Security headers
        headers_score, headers_metrics = await self.scorers['security_headers'].score(url)
        metrics['security_headers'] = headers_metrics
        total_score += headers_score * 0.3
        max_score += 0.3
        
        # Malware checks
        malware_score, malware_metrics = await self.scorers['malware'].score(url)
        metrics['malware'] = malware_metrics
        total_score += malware_score * 0.3
        max_score += 0.3
        
        final_score = total_score / max_score if max_score > 0 else 0.0
        
        return {
            'score': final_score,
            'metrics': metrics
        }
    
    async def _score_reputation_metrics(self, url: str) -> Dict[str, Any]:
        """Score reputation-related metrics."""
        metrics = {}
        total_score = 0.0
        max_score = 0.0
        
        # Domain reputation
        rep_score, rep_metrics = await self.scorers['domain_reputation'].score(url)
        metrics['domain_reputation'] = rep_metrics
        total_score += rep_score * 0.4
        max_score += 0.4
        
        # Domain age
        age_score, age_metrics = await self.scorers['domain_age'].score(url)
        metrics['domain_age'] = age_metrics
        total_score += age_score * 0.3
        max_score += 0.3
        
        # Incident tracking
        incident_score, incident_metrics = await self.scorers['incidents'].score(url)
        metrics['incidents'] = incident_metrics
        total_score += incident_score * 0.3
        max_score += 0.3
        
        final_score = total_score / max_score if max_score > 0 else 0.0
        
        return {
            'score': final_score,
            'metrics': metrics
        }
    
    async def _score_compliance_metrics(self, url: str) -> Dict[str, Any]:
        """Score compliance-related metrics."""
        metrics = {}
        total_score = 0.0
        max_score = 0.0
        
        # Privacy policy
        privacy_score, privacy_metrics = await self.scorers['privacy_policy'].score(url)
        metrics['privacy_policy'] = privacy_metrics
        total_score += privacy_score * 0.4
        max_score += 0.4
        
        # Contact validation
        contact_score, contact_metrics = await self.scorers['contact'].score(url)
        metrics['contact'] = contact_metrics
        total_score += contact_score * 0.3
        max_score += 0.3
        
        # Legal compliance
        compliance_score, compliance_metrics = await self.scorers['compliance'].score(url)
        metrics['compliance'] = compliance_metrics
        total_score += compliance_score * 0.3
        max_score += 0.3
        
        final_score = total_score / max_score if max_score > 0 else 0.0
        
        return {
            'score': final_score,
            'metrics': metrics
        }
    
    def _calculate_weighted_score(self, security_score: float, reputation_score: float, compliance_score: float) -> float:
        """Calculate final weighted score."""
        return (
            security_score * self.weights['security'] +
            reputation_score * self.weights['reputation'] +
            compliance_score * self.weights['compliance']
        )
    
    def _calculate_confidence(self, security_metrics: Dict, reputation_metrics: Dict, compliance_metrics: Dict) -> float:
        """Calculate confidence based on data completeness."""
        total_checks = 0
        successful_checks = 0
        
        # Count security checks
        for metric_name, metric_data in security_metrics.items():
            total_checks += 1
            if metric_data.get('success', False):
                successful_checks += 1
        
        # Count reputation checks
        for metric_name, metric_data in reputation_metrics.items():
            total_checks += 1
            if metric_data.get('success', False):
                successful_checks += 1
        
        # Count compliance checks
        for metric_name, metric_data in compliance_metrics.items():
            total_checks += 1
            if metric_data.get('success', False):
                successful_checks += 1
        
        return successful_checks / total_checks if total_checks > 0 else 0.0
    
    def get_trust_level_description(self, score: float) -> str:
        """Get human-readable description of trust level."""
        level = TrustLevel.from_score(score)
        return level.description
