# Trust Scoring System

The AiHint Trust Scoring System provides automated, comprehensive trust assessment for websites across **Python, PHP, and JavaScript** implementations, enabling AI systems to make informed decisions about content reliability and safety.

## Overview

The trust scoring system analyzes websites across three key dimensions with **enhanced capabilities**:

- **Security**: SSL/TLS configuration, security headers, malware detection
- **Reputation**: Domain age, historical incidents, third-party reputation, **enhanced incident tracking**
- **Compliance**: Privacy policies, contact information, legal compliance, **business registration validation**

## Cross-Platform Support

The trust scoring system is fully implemented across all platforms:

- **Python**: Complete async scoring engine with detailed analysis
- **PHP**: Production-ready scoring with Composer integration  
- **JavaScript**: Modern web-optimized scoring with TypeScript support
- **Consistent API**: Unified scoring interface across all platforms

## Quick Start

### Basic Scoring

Score a single website:

```bash
aihint scoring score https://example.com
```

Score with verbose output:

```bash
aihint scoring score https://example.com --verbose
```

### Batch Scoring

Score multiple websites:

```bash
aihint scoring batch --urls https://example.com,https://github.com,https://stackoverflow.com
```

### Automated AiHint Generation

Create an AiHint with automated scoring:

```bash
aihint create-with-score \
  --target "https://example.com" \
  --issuer "https://trust.aihint.org" \
  --public-key-url "https://trust.aihint.org/pubkey.pem" \
  --verbose \
  --output "scored_aihint.json"
```

## Enhanced Features (v1.1.0)

### Phase 2 Enhancements - Advanced Incident Tracking

The reputation analysis now includes **4 new incident detection capabilities**:

- **Data Breach Detection**: Historical data breach checking and pattern analysis
- **Malware History Tracking**: Domain malware incident analysis and risk assessment  
- **Phishing Incident Analysis**: Phishing history tracking and domain pattern recognition
- **Regulatory Violation Detection**: Compliance violation tracking and pattern analysis

### Phase 3 Enhancements - Advanced Compliance Validation

The compliance analysis now includes **enhanced business validation**:

- **Business Registration Validation**: Advanced business legitimacy assessment
  - Business indicator detection in URLs and content
  - Corporate structure analysis and legal entity verification
  - Professional contact validation and social media presence analysis
- **Regulatory Compliance Analysis**: Enhanced compliance framework assessment
  - GDPR/CCPA compliance indicator detection
  - Regulatory keyword analysis and pattern recognition
  - Compliance mechanism evaluation and scoring
- **Data Protection Compliance**: Improved privacy and data handling assessment
  - Privacy policy quality analysis and content evaluation
  - Data handling transparency assessment
  - Protection mechanism evaluation and scoring

### Performance Improvements

- **+7.9% improvement** in average trust scores (0.580 → 0.626)
- **+33% better consistency** with reduced score variance across platforms
- **90% specification compliance** achieved (up from 83%)
- **Enhanced Phase 2**: 85% compliance (+15% improvement)
- **Enhanced Phase 3**: 90% compliance (+7% improvement)

## Scoring Methodology

### Phase 1: Core Security Metrics

#### SSL/TLS Validation
- Certificate validity and expiration
- Cipher strength and protocol versions
- Certificate chain validation
- HSTS (HTTP Strict Transport Security) presence

#### Security Headers Analysis
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

#### Malware and Phishing Detection
- Google Safe Browsing API integration
- VirusTotal database checks
- PhishTank phishing detection
- Real-time threat intelligence

#### Domain Reputation
- WHOIS analysis and domain information
- Blacklist checking
- Domain registration details
- Registrar reputation

### Phase 2: Reputation Signals

#### Domain Age Analysis
- Registration date analysis
- Domain maturity scoring
- Historical stability assessment

#### Historical Incident Tracking
- Security breach history
- Downtime incidents
- Reputation degradation events

#### Third-Party Reputation APIs
- External reputation services
- Community trust indicators
- Industry-specific assessments

### Phase 3: Content & Compliance

#### Privacy Policy Detection
- Privacy policy presence and accessibility
- GDPR compliance indicators
- Data handling transparency

#### Contact Information Validation
- Contact details verification
- Business registration validation
- Physical address verification

#### Legal Compliance Indicators
- Terms of service presence
- Legal entity verification
- Regulatory compliance checks

## Trust Levels

The system classifies websites into five trust levels:

| Trust Level | Score Range | Description |
|-------------|-------------|-------------|
| **Highly Trusted** | 0.9-1.0 | Banks, major corporations, verified entities |
| **Good Trust** | 0.7-0.89 | Legitimate businesses, established sites |
| **Moderate Trust** | 0.5-0.69 | Newer sites, some concerns |
| **Low Trust** | 0.3-0.49 | Multiple red flags, proceed with caution |
| **Very Low Trust** | 0.0-0.29 | Malicious, compromised, or highly suspicious |

## Configuration

### Default Configuration

The system uses sensible defaults, but you can customize scoring behavior:

```bash
# Generate sample configuration
aihint scoring config --output scoring_config.json
```

### Custom Configuration

```json
{
  "timeout": 30,
  "weights": {
    "security": 0.4,
    "reputation": 0.35,
    "compliance": 0.25
  },
  "scorers": {
    "ssl_tls": {
      "enabled": true,
      "weight": 0.3,
      "min_cipher_strength": 128
    },
    "security_headers": {
      "enabled": true,
      "weight": 0.2,
      "required_headers": ["HSTS", "CSP"]
    },
    "malware": {
      "enabled": true,
      "weight": 0.3,
      "apis": {
        "google_safe_browsing": true,
        "virustotal": true,
        "phishtank": true
      }
    },
    "domain_reputation": {
      "enabled": true,
      "weight": 0.2
    },
    "domain_age": {
      "enabled": true,
      "weight": 0.15,
      "min_age_days": 30
    },
    "incidents": {
      "enabled": true,
      "weight": 0.1
    },
    "privacy_policy": {
      "enabled": true,
      "weight": 0.1
    },
    "contact": {
      "enabled": true,
      "weight": 0.1
    },
    "compliance": {
      "enabled": true,
      "weight": 0.05
    }
  }
}
```

### Using Custom Configuration

```bash
aihint scoring score https://example.com --config my_config.json
aihint create-with-score --target https://example.com --config my_config.json
```

## Output Formats

### Text Format (Default)
```
Website: https://example.com
Trust Score: 0.688 (MODERATE)
Confidence: 1.000

Security Score: 0.488
- SSL/TLS: 0.600
- Security Headers: 0.300
- Malware Check: 0.500
- Domain Reputation: 0.400

Reputation Score: 0.958
- Domain Age: 0.900
- Incidents: 1.000

Compliance Score: 0.632
- Privacy Policy: 0.500
- Contact Info: 0.800
- Legal Compliance: 0.600
```

### Table Format
```bash
aihint scoring score https://example.com --format table
```

### JSON Format
```bash
aihint scoring score https://example.com --format json
```

## Integration Examples

### Python API

```python
from aihint.scoring import TrustScoringEngine
import asyncio

async def score_website():
    engine = TrustScoringEngine()
    result = await engine.score_website("https://example.com")
    
    print(f"Trust Score: {result.final_score}")
    print(f"Trust Level: {result.trust_level.name}")
    print(f"Security: {result.security_score}")
    print(f"Reputation: {result.reputation_score}")
    print(f"Compliance: {result.compliance_score}")

# Run the scoring
asyncio.run(score_website())
```

### Batch Processing

```python
from aihint.scoring import TrustScoringEngine
import asyncio

async def batch_score():
    engine = TrustScoringEngine()
    urls = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com"
    ]
    
    results = await engine.score_websites(urls)
    
    for result in results:
        print(f"{result.url}: {result.final_score:.3f} ({result.trust_level.name})")

asyncio.run(batch_score())
```

## Performance Considerations

### Timeouts
- Default timeout: 30 seconds per website
- Configurable per scorer and overall
- Graceful degradation on timeouts

### Rate Limiting
- Respects API rate limits for external services
- Implements exponential backoff
- Caches results to reduce API calls

### Caching
- Results cached for 1 hour by default
- Configurable cache duration
- Cache invalidation on errors

## Troubleshooting

### Common Issues

#### SSL Certificate Errors
```
Error: SSL certificate verification failed
```
**Solution**: Check if the website has valid SSL certificates

#### API Rate Limiting
```
Error: Rate limit exceeded for Google Safe Browsing API
```
**Solution**: Wait and retry, or disable specific APIs in configuration

#### Network Timeouts
```
Error: Request timeout after 30 seconds
```
**Solution**: Increase timeout in configuration or check network connectivity

#### Domain Resolution Issues
```
Error: Failed to resolve domain
```
**Solution**: Check DNS configuration and domain validity

### Debug Mode

Enable verbose output for debugging:

```bash
aihint scoring score https://example.com --verbose
```

### Logging

The system uses Python's logging module. Configure logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### For AI Systems
1. **Cache Results**: Store scoring results to avoid repeated analysis
2. **Set Thresholds**: Define minimum trust scores for different use cases
3. **Monitor Changes**: Re-score websites periodically as trust can change
4. **Combine Sources**: Use multiple trust indicators for critical decisions

### For Website Owners
1. **Implement Security Headers**: Use proper CSP, HSTS, and other security headers
2. **Maintain SSL Certificates**: Ensure certificates are valid and properly configured
3. **Provide Contact Information**: Make contact details easily accessible
4. **Create Privacy Policies**: Implement clear, accessible privacy policies

### For Developers
1. **Handle Errors Gracefully**: Implement proper error handling for scoring failures
2. **Use Configuration**: Customize scoring weights based on your use case
3. **Monitor Performance**: Track scoring performance and optimize as needed
4. **Update Regularly**: Keep scoring modules updated with latest threat intelligence

## See Also

- [CLI Reference](../api-reference/cli-reference.md) - Command-line interface details
- [Python API](../api-reference/python-api.md) - Python implementation details
- [Security Considerations](../technical/security-considerations.md) - Security best practices
- [Trust Model](../technical/trust-model.md) - Trust model architecture
