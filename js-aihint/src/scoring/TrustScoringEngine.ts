import { SecurityMetrics } from './Metrics/SecurityMetrics';
import { ReputationMetrics } from './Metrics/ReputationMetrics';
import { ComplianceMetrics } from './Metrics/ComplianceMetrics';
import { ScoringResult } from './ScoringResult';
import { TrustLevel } from './TrustLevel';

export interface ScoringConfig {
  timeouts: {
    http: number;
    dns: number;
    ssl: number;
  };
  apiKeys: {
    googleSafeBrowsing?: string;
    virusTotal?: string;
    phishTank?: string;
  };
  weights: {
    security: number;
    reputation: number;
    compliance: number;
  };
}

export class TrustScoringEngine {
  private securityMetrics: SecurityMetrics;
  private reputationMetrics: ReputationMetrics;
  private complianceMetrics: ComplianceMetrics;
  private config: ScoringConfig;

  constructor(config?: Partial<ScoringConfig>) {
    this.config = {
      timeouts: {
        http: 10000,
        dns: 5000,
        ssl: 5000,
        ...config?.timeouts
      },
      apiKeys: {
        ...config?.apiKeys
      },
      weights: {
        security: 0.4,
        reputation: 0.35,
        compliance: 0.25,
        ...config?.weights
      }
    };

    this.securityMetrics = new SecurityMetrics(this.config);
    this.reputationMetrics = new ReputationMetrics(this.config);
    this.complianceMetrics = new ComplianceMetrics(this.config);
  }

  async scoreWebsite(url: string): Promise<ScoringResult> {
    const startTime = Date.now();
    
    try {
      // Run all metric collections in parallel
      const [securityResult, reputationResult, complianceResult] = await Promise.all([
        this.securityMetrics.collect(url),
        this.reputationMetrics.collect(url),
        this.complianceMetrics.collect(url)
      ]);

      // Calculate weighted final score
      const finalScore = 
        (securityResult.score * this.config.weights.security) +
        (reputationResult.score * this.config.weights.reputation) +
        (complianceResult.score * this.config.weights.compliance);

      // Determine trust level
      const trustLevel = this.determineTrustLevel(finalScore);

      // Calculate confidence based on successful checks
      const totalChecks = securityResult.metrics.length + 
                         reputationResult.metrics.length + 
                         complianceResult.metrics.length;
      const successfulChecks = securityResult.metrics.filter(m => m.status === 'SUCCESS').length +
                              reputationResult.metrics.filter(m => m.status === 'SUCCESS').length +
                              complianceResult.metrics.filter(m => m.status === 'SUCCESS').length;
      const confidence = totalChecks > 0 ? successfulChecks / totalChecks : 0;

      // Collect all warnings and errors
      const allWarnings = [
        ...securityResult.warnings,
        ...reputationResult.warnings,
        ...complianceResult.warnings
      ];
      const allErrors = [
        ...securityResult.errors,
        ...reputationResult.errors,
        ...complianceResult.errors
      ];

      // Collect all detailed metrics
      const detailedMetrics = [
        ...securityResult.metrics,
        ...reputationResult.metrics,
        ...complianceResult.metrics
      ];

      return new ScoringResult({
        url,
        finalScore,
        trustLevel,
        confidence,
        securityScore: securityResult.score,
        reputationScore: reputationResult.score,
        complianceScore: complianceResult.score,
        detailedMetrics,
        warnings: allWarnings,
        errors: allErrors,
        executionTime: Date.now() - startTime
      });

    } catch (error) {
      return new ScoringResult({
        url,
        finalScore: 0,
        trustLevel: TrustLevel.VERY_LOW,
        confidence: 0,
        securityScore: 0,
        reputationScore: 0,
        complianceScore: 0,
        detailedMetrics: [],
        warnings: [],
        errors: [`Scoring failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        executionTime: Date.now() - startTime
      });
    }
  }

  private determineTrustLevel(score: number): TrustLevel {
    if (score >= 0.8) return TrustLevel.HIGH;
    if (score >= 0.6) return TrustLevel.GOOD;
    if (score >= 0.4) return TrustLevel.MODERATE;
    if (score >= 0.2) return TrustLevel.LOW;
    return TrustLevel.VERY_LOW;
  }
}
