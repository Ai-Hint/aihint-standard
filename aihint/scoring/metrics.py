"""
Scoring Metrics Framework

Base classes and data structures for different types of scoring metrics.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class MetricStatus(Enum):
    """Status of a metric check."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class MetricResult:
    """Result of a single metric check."""
    name: str
    status: MetricStatus
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    execution_time_ms: float


class BaseMetrics(ABC):
    """Base class for all metric collectors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.results: List[MetricResult] = []
    
    @abstractmethod
    async def collect_metrics(self, url: str) -> List[MetricResult]:
        """Collect all metrics for the given URL."""
        pass
    
    def calculate_overall_score(self) -> float:
        """Calculate overall score from collected metrics."""
        if not self.results:
            return 0.0
        
        # Weighted average of all successful metrics
        total_weight = 0.0
        weighted_sum = 0.0
        
        for result in self.results:
            if result.status == MetricStatus.SUCCESS:
                weight = result.details.get('weight', 1.0)
                weighted_sum += result.score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_successful_metrics(self) -> List[MetricResult]:
        """Get all successfully collected metrics."""
        return [r for r in self.results if r.status == MetricStatus.SUCCESS]
    
    def get_failed_metrics(self) -> List[MetricResult]:
        """Get all failed metrics."""
        return [r for r in self.results if r.status in [MetricStatus.ERROR, MetricStatus.WARNING]]


class SecurityMetrics(BaseMetrics):
    """Security-related metrics collector."""
    
    async def collect_metrics(self, url: str) -> List[MetricResult]:
        """Collect security metrics for the URL."""
        self.results = []
        
        # This will be implemented by individual security scorers
        # For now, return empty list - actual implementation in scorers
        return self.results


class ReputationMetrics(BaseMetrics):
    """Reputation-related metrics collector."""
    
    async def collect_metrics(self, url: str) -> List[MetricResult]:
        """Collect reputation metrics for the URL."""
        self.results = []
        
        # This will be implemented by individual reputation scorers
        # For now, return empty list - actual implementation in scorers
        return self.results


class ComplianceMetrics(BaseMetrics):
    """Compliance-related metrics collector."""
    
    async def collect_metrics(self, url: str) -> List[MetricResult]:
        """Collect compliance metrics for the URL."""
        self.results = []
        
        # This will be implemented by individual compliance scorers
        # For now, return empty list - actual implementation in scorers
        return self.results
