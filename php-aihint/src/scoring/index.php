<?php
namespace AIHint\Scoring;

// Main scoring system entry point
require_once __DIR__ . '/TrustScoringEngine.php';
require_once __DIR__ . '/ScoringResult.php';
require_once __DIR__ . '/TrustLevel.php';
require_once __DIR__ . '/Metrics/BaseMetrics.php';
require_once __DIR__ . '/Metrics/MetricResult.php';
require_once __DIR__ . '/Metrics/MetricStatus.php';
require_once __DIR__ . '/Metrics/SecurityMetrics.php';
require_once __DIR__ . '/Metrics/ReputationMetrics.php';
require_once __DIR__ . '/Metrics/ComplianceMetrics.php';
require_once __DIR__ . '/Scorers/BaseScorer.php';
require_once __DIR__ . '/Scorers/SSLTLSValidator.php';
require_once __DIR__ . '/Scorers/SecurityHeadersAnalyzer.php';
require_once __DIR__ . '/Scorers/MalwareChecker.php';
require_once __DIR__ . '/Scorers/DomainReputationChecker.php';
require_once __DIR__ . '/Scorers/DomainAgeAnalyzer.php';
require_once __DIR__ . '/Scorers/IncidentTracker.php';
require_once __DIR__ . '/Scorers/PrivacyPolicyAnalyzer.php';
require_once __DIR__ . '/Scorers/ContactValidator.php';
require_once __DIR__ . '/Scorers/ComplianceChecker.php';

// Export main classes
class_alias('AIHint\Scoring\TrustScoringEngine', 'AIHint\Scoring\Engine');
class_alias('AIHint\Scoring\ScoringResult', 'AIHint\Scoring\Result');
class_alias('AIHint\Scoring\TrustLevel', 'AIHint\Scoring\Level');
