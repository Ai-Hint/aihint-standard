# AiHint Trust Scoring System

A comprehensive trust scoring system that evaluates websites based on security metrics, reputation signals, and compliance indicators.

## Overview

The AiHint Trust Scoring System provides automated trust assessment for websites using a multi-layered approach:

- **Phase 1: Core Security Metrics** - SSL/TLS validation, security headers, malware checks
- **Phase 2: Reputation Signals** - Domain age analysis, incident tracking, reputation databases
- **Phase 3: Content & Compliance** - Privacy policies, contact information, legal compliance

## Quick Start

### Basic Usage

```python
from aihint.scoring import TrustScoringEngine

# Initialize the scoring engine
engine = TrustScoringEngine()

# Score a website
result = await engine.score_website("https://example.com")

print(f"Trust Score: {result.final_score:.3f}")
print(f"Trust Level: {result.trust_level.name}")
print(f"Confidence: {result.confidence:.3f}")
```

### CLI Usage

```bash
# Score a single website
aihint scoring score https://example.com

# Score multiple websites
aihint scoring batch https://example.com https://github.com

# Generate sample configuration
aihint scoring config --output config.json

# Use custom configuration
aihint scoring score https://example.com --config config.json --output results.json
```

## Trust Score Interpretation

| Score Range | Trust Level | Description |
|-------------|-------------|-------------|
| 0.9-1.0 | HIGH | Highly trusted (banks, major corporations, verified entities) |
| 0.7-0.89 | GOOD | Good trust (legitimate businesses, established sites) |
| 0.5-0.69 | MODERATE | Moderate trust (newer sites, some concerns) |
| 0.3-0.49 | LOW | Low trust (multiple red flags, proceed with caution) |
| 0.0-0.29 | VERY_LOW | Very low trust (malicious, compromised, or highly suspicious) |

## Configuration

### Basic Configuration

```json
{
  "ssl": {
    "timeout": 10
  },
  "headers": {
    "timeout": 10
  },
  "malware": {
    "timeout": 10,
    "google_safe_browsing": {
      "enabled": false,
      "api_key": "YOUR_API_KEY_HERE"
    },
    "virustotal": {
      "enabled": false,
      "api_key": "YOUR_API_KEY_HERE"
    },
    "phishtank": {
      "enabled": false
    }
  }
}
```

### API Keys Setup

To enable real-time malware and reputation checks, you'll need API keys:

1. **Google Safe Browsing API**
   - Get API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Safe Browsing API
   - Add to config: `"google_safe_browsing": {"enabled": true, "api_key": "YOUR_KEY"}`

2. **VirusTotal API**
   - Get API key from [VirusTotal](https://www.virustotal.com/gui/my-apikey)
   - Add to config: `"virustotal": {"enabled": true, "api_key": "YOUR_KEY"}`

3. **PhishTank**
   - Free service, no API key required
   - Add to config: `"phishtank": {"enabled": true}`

## Scoring Components

### Phase 1: Security Metrics (40% weight)

#### SSL/TLS Validation
- Certificate validity and expiration
- Cipher strength analysis
- Protocol version support
- Certificate chain completeness

#### Security Headers
- HSTS (HTTP Strict Transport Security)
- CSP (Content Security Policy)
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

#### Malware & Phishing Checks
- Google Safe Browsing API
- VirusTotal integration
- PhishTank database
- Suspicious pattern detection

### Phase 2: Reputation Signals (35% weight)

#### Domain Reputation
- WHOIS data analysis
- Blacklist checking
- DNS reputation analysis

#### Domain Age Analysis
- Registration date
- Historical changes
- Registrar reputation

#### Incident Tracking
- Security incident history
- Downtime analysis
- SSL incident tracking

### Phase 3: Compliance (25% weight)

#### Privacy Policy Analysis
- Policy presence and accessibility
- GDPR compliance indicators
- CCPA compliance indicators
- Content quality analysis

#### Contact Information Validation
- Email address verification
- Phone number validation
- Physical address checking
- Contact page analysis

#### Legal Compliance
- Terms of service analysis
- Cookie compliance
- Accessibility compliance
- Legal notices

## Advanced Usage

### Custom Scoring Weights

```python
engine = TrustScoringEngine({
    'weights': {
        'security': 0.5,      # 50% weight for security
        'reputation': 0.3,    # 30% weight for reputation
        'compliance': 0.2     # 20% weight for compliance
    }
})
```

### Individual Scorer Usage

```python
from aihint.scoring.scorers import SSLTLSValidator, SecurityHeadersAnalyzer

# Use individual scorers
ssl_validator = SSLTLSValidator()
ssl_score, ssl_metrics = await ssl_validator.score("https://example.com")

headers_analyzer = SecurityHeadersAnalyzer()
headers_score, headers_metrics = await headers_analyzer.score("https://example.com")
```

### Batch Processing

```python
import asyncio

async def score_multiple_urls(urls):
    engine = TrustScoringEngine()
    
    # Score all URLs concurrently
    tasks = [engine.score_website(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    return results

# Usage
urls = ["https://example.com", "https://github.com", "https://stackoverflow.com"]
results = await score_multiple_urls(urls)
```

## Output Format

### ScoringResult Object

```python
@dataclass
class ScoringResult:
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
    method: str
```

### Detailed Metrics Structure

```json
{
  "security": {
    "ssl_tls": {
      "ssl_tls_score": 0.85,
      "checks": [...],
      "success": true
    },
    "security_headers": {
      "security_headers_score": 0.72,
      "headers_analyzed": 8,
      "headers_present": 6,
      "header_details": [...]
    },
    "malware": {
      "malware_score": 1.0,
      "threats_found": [],
      "checks_performed": 5
    }
  },
  "reputation": {
    "domain_reputation": {...},
    "domain_age": {...},
    "incidents": {...}
  },
  "compliance": {
    "privacy_policy": {...},
    "contact": {...},
    "compliance": {...}
  }
}
```

## Performance Considerations

- **Concurrent Processing**: All checks run in parallel for maximum speed
- **Caching**: Results can be cached to avoid repeated checks
- **Timeouts**: Configurable timeouts prevent hanging requests
- **Rate Limiting**: Built-in rate limiting for API calls

## Error Handling

The scoring system includes comprehensive error handling:

- **Network Errors**: Graceful handling of connection issues
- **API Failures**: Fallback behavior when external APIs fail
- **Invalid URLs**: Proper validation and error reporting
- **Timeout Handling**: Configurable timeouts with fallbacks

## Contributing

To add new scoring metrics:

1. Create a new scorer in `scorers/`
2. Implement the `score(url)` method
3. Add to the appropriate phase in `engine.py`
4. Update configuration schema
5. Add tests

## License

MIT License - see main project license file.
