import { BaseMetrics } from './BaseMetrics';
import { MetricResult, MetricStatus } from './MetricResult';
import { DomainReputationChecker } from '../Scorers/DomainReputationChecker';
import { DomainAgeAnalyzer } from '../Scorers/DomainAgeAnalyzer';
import { IncidentTracker } from '../Scorers/IncidentTracker';

export class ReputationMetrics extends BaseMetrics {
  private reputationChecker: DomainReputationChecker;
  private ageAnalyzer: DomainAgeAnalyzer;
  private incidentTracker: IncidentTracker;

  constructor(config: any) {
    super(config);
    this.reputationChecker = new DomainReputationChecker(config);
    this.ageAnalyzer = new DomainAgeAnalyzer(config);
    this.incidentTracker = new IncidentTracker(config);
  }

  async collect(url: string): Promise<{
    score: number;
    metrics: MetricResult[];
    warnings: string[];
    errors: string[];
  }> {
    this.metrics = [];
    this.warnings = [];
    this.errors = [];

    try {
      // Run reputation checks in parallel
      const [reputationResult, ageResult, incidentResult] = await Promise.all([
        this.reputationChecker.score(url),
        this.ageAnalyzer.score(url),
        this.incidentTracker.score(url)
      ]);

      // Add all metrics
      this.metrics.push(...reputationResult.metrics);
      this.metrics.push(...ageResult.metrics);
      this.metrics.push(...incidentResult.metrics);

      // Add warnings and errors
      this.warnings.push(...reputationResult.warnings);
      this.warnings.push(...ageResult.warnings);
      this.warnings.push(...incidentResult.warnings);

      this.errors.push(...reputationResult.errors);
      this.errors.push(...ageResult.errors);
      this.errors.push(...incidentResult.errors);

      // Calculate weighted score
      const reputationWeight = 0.5;
      const ageWeight = 0.3;
      const incidentWeight = 0.2;

      const score = (reputationResult.score * reputationWeight) + 
                   (ageResult.score * ageWeight) + 
                   (incidentResult.score * incidentWeight);

      return {
        score: Math.max(0, Math.min(1, score)),
        metrics: this.metrics,
        warnings: this.warnings,
        errors: this.errors
      };

    } catch (error) {
      this.addError(`Reputation metrics collection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return {
        score: 0,
        metrics: this.metrics,
        warnings: this.warnings,
        errors: this.errors
      };
    }
  }
}
