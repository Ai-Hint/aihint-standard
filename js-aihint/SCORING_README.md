# AiHint Trust Scoring for JavaScript/TypeScript

This directory contains the JavaScript/TypeScript implementation of the AiHint trust scoring system, fully integrated with the existing AiHint protocol implementation.

## Features

- **Complete Trust Scoring Engine**: Multi-layered scoring based on security, reputation, and compliance metrics
- **AiHint Integration**: Seamlessly generates AiHint metadata with trust scores
- **TypeScript Support**: Full type safety and IntelliSense support
- **CLI Interface**: Command-line tools for scoring and batch processing
- **Modular Architecture**: Extensible scorer system for custom metrics

## Quick Start

### Installation

```bash
npm install
```

### Basic Usage

```typescript
import { TrustScoringEngine } from './src/scoring';
import { signHint } from './src/aihint';

// Initialize scoring engine
const scoringEngine = new TrustScoringEngine();

// Score a website
const result = await scoringEngine.scoreWebsite('https://github.com');

// Create AiHint with trust score
const aihintData = {
  version: '0.1',
  type: 'global',
  target: 'https://github.com',
  issuer: 'https://trust.aihint.org',
  score: result.finalScore,
  method: 'aihint-scoring-v1', // Use scoring method
  issued_at: new Date().toISOString(),
  expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
  comment: `Trust score: ${result.finalScore} (Level: ${result.trustLevel})`,
  public_key_url: 'https://trust.aihint.org/pubkey.pem'
};

// Sign the AiHint
const signedAiHint = signHint(aihintData, 'private_key.pem');
```

### CLI Usage

```bash
# Score a single URL
npm run scoring score https://github.com --verbose

# Score multiple URLs
npm run scoring batch --urls "https://github.com,https://stackoverflow.com" --output results.json

# Generate configuration
npm run scoring config --output my-config.json
```

## Scoring Components

### Security Metrics (40% weight)
- **SSL/TLS Validation**: Certificate validity, TLS version, HSTS headers
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options, etc.
- **Malware Detection**: Integration with security APIs (Google Safe Browsing, VirusTotal)

### Reputation Metrics (35% weight)
- **Domain Reputation**: Blacklist checks, historical reputation
- **Domain Age**: Registration date and stability analysis
- **Incident Tracking**: Security incident history

### Compliance Metrics (25% weight)
- **Privacy Policy**: Presence and content analysis
- **Contact Information**: Accessibility and completeness
- **Legal Compliance**: Terms of service, accessibility compliance

## Trust Levels

- **HIGH (0.8-1.0)**: Verified, highly reputable
- **GOOD (0.6-0.8)**: Legitimate businesses, established sites
- **MODERATE (0.4-0.6)**: Newer sites, some concerns
- **LOW (0.2-0.4)**: Unreliable, proceed with caution
- **VERY_LOW (0.0-0.2)**: Suspicious, potentially harmful

## Configuration

```typescript
const config = {
  timeouts: {
    http: 10000,
    dns: 5000,
    ssl: 5000
  },
  apiKeys: {
    googleSafeBrowsing: 'YOUR_API_KEY',
    virusTotal: 'YOUR_API_KEY',
    phishTank: 'YOUR_API_KEY'
  },
  weights: {
    security: 0.4,
    reputation: 0.35,
    compliance: 0.25
  }
};

const scoringEngine = new TrustScoringEngine(config);
```

## Examples

### Complete Workflow

See `examples/complete_aihint_workflow.ts` for a full example that:
1. Calculates trust score
2. Creates AiHint metadata
3. Signs with private key
4. Verifies signature
5. Saves to file

### Batch Processing

See `examples/scoring_to_aihint.ts` for batch processing multiple URLs.

## API Reference

### TrustScoringEngine

```typescript
class TrustScoringEngine {
  constructor(config?: Partial<ScoringConfig>);
  scoreWebsite(url: string): Promise<ScoringResult>;
}
```

### ScoringResult

```typescript
interface ScoringResult {
  url: string;
  finalScore: number;
  trustLevel: TrustLevel;
  confidence: number;
  securityScore: number;
  reputationScore: number;
  complianceScore: number;
  detailedMetrics: MetricResult[];
  warnings: string[];
  errors: string[];
  executionTime: number;
}
```

## Integration with AiHint

The scoring system is fully integrated with the existing AiHint protocol:

- Uses `method: "aihint-scoring-v1"` to identify scoring method
- Populates `score` field with calculated trust score
- Includes trust level in `comment` field
- Maintains full compatibility with AiHint validation and verification

## Development

### Building

```bash
# Build all TypeScript files
npm run build

# Build only scoring system
npm run build:scoring
```

### Adding Custom Scorers

1. Extend `BaseScorer` class
2. Implement `score(url: string): Promise<ScorerResult>` method
3. Add to appropriate metrics collector (Security, Reputation, or Compliance)

```typescript
export class CustomScorer extends BaseScorer {
  async score(url: string): Promise<ScorerResult> {
    // Your scoring logic here
    return this.getResult(score);
  }
}
```

## License

ISC License - see main project LICENSE file.
