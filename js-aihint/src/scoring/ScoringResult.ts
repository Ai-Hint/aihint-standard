import { TrustLevel, TrustLevelHelper } from './TrustLevel';
import { MetricResult } from './Metrics/MetricResult';

export interface ScoringResultData {
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

export class ScoringResult {
  public readonly url: string;
  public readonly finalScore: number;
  public readonly trustLevel: TrustLevel;
  public readonly confidence: number;
  public readonly securityScore: number;
  public readonly reputationScore: number;
  public readonly complianceScore: number;
  public readonly detailedMetrics: MetricResult[];
  public readonly warnings: string[];
  public readonly errors: string[];
  public readonly executionTime: number;
  public readonly timestamp: string;
  public readonly method: string = 'aihint-scoring-v1';

  constructor(data: ScoringResultData) {
    this.url = data.url;
    this.finalScore = data.finalScore;
    this.trustLevel = data.trustLevel;
    this.confidence = data.confidence;
    this.securityScore = data.securityScore;
    this.reputationScore = data.reputationScore;
    this.complianceScore = data.complianceScore;
    this.detailedMetrics = data.detailedMetrics;
    this.warnings = data.warnings;
    this.errors = data.errors;
    this.executionTime = data.executionTime;
    this.timestamp = new Date().toISOString();
  }

  toJSON(): any {
    return {
      url: this.url,
      final_score: this.finalScore,
      trust_level: this.trustLevel,
      trust_level_description: TrustLevelHelper.getDescription(this.trustLevel),
      confidence: this.confidence,
      security_score: this.securityScore,
      reputation_score: this.reputationScore,
      compliance_score: this.complianceScore,
      detailed_metrics: this.detailedMetrics.map(m => m.toJSON()),
      warnings: this.warnings,
      errors: this.errors,
      timestamp: this.timestamp,
      method: this.method
    };
  }
}
