# AiHint PHP Implementation

This is a comprehensive PHP implementation of the AiHint protocol for creating, signing, validating, and verifying AiHint metadata, plus a complete trust scoring system for website analysis.

## Install

```
composer install
```

## Usage

```php
require_once 'src/AIHint.php';
use AIHint\AIHint;

$hint = [
    "version" => "0.1",
    "type" => "global",
    "target" => "https://example.com",
    "issuer" => "https://trust.aihint.org",
    "score" => 0.92,
    "method" => "aihint-core-v1",
    "issued_at" => "2025-01-01T12:00:00Z",
    "expires_at" => "2026-01-01T00:00:00Z",
    "comment" => "Example AiHint for demonstration",
    "public_key_url" => "https://trust.aihint.org/pubkey.pem"
];

$signed = AIHint::signHint($hint, 'private_key.pem');
print_r($signed);

$valid = AIHint::verifyHint($signed, 'public_key.pem');
echo "Signature valid? " . ($valid ? 'true' : 'false') . "\n";

$schemaValid = AIHint::validateHint($signed);
echo "Schema valid? " . ($schemaValid ? 'true' : 'false') . "\n";
```

## Trust Scoring System

The PHP implementation includes a comprehensive trust scoring system that evaluates websites based on security metrics, reputation signals, and compliance indicators.

### Quick Start

```php
require_once 'src/scoring/index.php';
use AIHint\Scoring\TrustScoringEngine;

// Initialize the scoring engine
$engine = new TrustScoringEngine();

// Score a website
$result = $engine->scoreWebsite('https://example.com');

echo "Trust Score: " . $result->finalScore . "\n";
echo "Trust Level: " . $result->trustLevel->name . "\n";
echo "Confidence: " . $result->confidence . "\n";
```

### CLI Usage

```bash
# Score a single website
./bin/aihint-scoring score https://example.com

# Score with verbose output
./bin/aihint-scoring score https://example.com --verbose

# Score multiple websites
./bin/aihint-scoring batch --urls https://example.com,https://github.com

# Generate sample configuration
./bin/aihint-scoring config --output config.json

# Use custom configuration
./bin/aihint-scoring score https://example.com --config config.json --output results.json
```

### Trust Score Interpretation

| Score Range | Trust Level | Description |
|-------------|-------------|-------------|
| 0.9-1.0 | HIGH | Highly trusted (banks, major corporations, verified entities) |
| 0.7-0.89 | GOOD | Good trust (legitimate businesses, established sites) |
| 0.5-0.69 | MODERATE | Moderate trust (newer sites, some concerns) |
| 0.3-0.49 | LOW | Low trust (multiple red flags, proceed with caution) |
| 0.0-0.29 | VERY_LOW | Very low trust (malicious, compromised, or highly suspicious) |

### Scoring Components

#### Phase 1: Security Metrics (40% weight)
- **SSL/TLS Validation**: Certificate validity, cipher strength, HSTS
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options, etc.
- **Malware Detection**: Google Safe Browsing, VirusTotal, PhishTank integration

#### Phase 2: Reputation Signals (35% weight)
- **Domain Reputation**: WHOIS analysis, blacklist checking, DNS reputation
- **Domain Age**: Registration date analysis, historical stability
- **Incident Tracking**: Security incidents, downtime analysis, SSL issues

#### Phase 3: Compliance (25% weight)
- **Privacy Policy**: GDPR/CCPA compliance, content quality analysis
- **Contact Information**: Email, phone, address validation
- **Legal Compliance**: Terms of service, cookie compliance, accessibility

### Configuration

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
  },
  "weights": {
    "security": 0.4,
    "reputation": 0.35,
    "compliance": 0.25
  }
}
```

### API Keys Setup

To enable real-time malware and reputation checks:

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

## Examples

### Basic AiHint Usage

See `examples/create_hint.php` for a full example of creating and verifying AiHints.

### Trust Scoring Examples

See `examples/scoring_example.php` for comprehensive examples of the trust scoring system.

## License

MIT License - see main project license file.
