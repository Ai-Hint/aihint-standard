import { BaseMetrics } from './BaseMetrics';
import { MetricResult, MetricStatus } from './MetricResult';
import { PrivacyPolicyAnalyzer } from '../Scorers/PrivacyPolicyAnalyzer';
import { ContactValidator } from '../Scorers/ContactValidator';
import { ComplianceChecker } from '../Scorers/ComplianceChecker';

export class ComplianceMetrics extends BaseMetrics {
  private privacyAnalyzer: PrivacyPolicyAnalyzer;
  private contactValidator: ContactValidator;
  private complianceChecker: ComplianceChecker;

  constructor(config: any) {
    super(config);
    this.privacyAnalyzer = new PrivacyPolicyAnalyzer(config);
    this.contactValidator = new ContactValidator(config);
    this.complianceChecker = new ComplianceChecker(config);
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
      // Run compliance checks in parallel
      const [privacyResult, contactResult, complianceResult] = await Promise.all([
        this.privacyAnalyzer.score(url),
        this.contactValidator.score(url),
        this.complianceChecker.score(url)
      ]);

      // Add all metrics
      this.metrics.push(...privacyResult.metrics);
      this.metrics.push(...contactResult.metrics);
      this.metrics.push(...complianceResult.metrics);

      // Add warnings and errors
      this.warnings.push(...privacyResult.warnings);
      this.warnings.push(...contactResult.warnings);
      this.warnings.push(...complianceResult.warnings);

      this.errors.push(...privacyResult.errors);
      this.errors.push(...contactResult.errors);
      this.errors.push(...complianceResult.errors);

      // Calculate weighted score
      const privacyWeight = 0.4;
      const contactWeight = 0.35;
      const complianceWeight = 0.25;

      const score = (privacyResult.score * privacyWeight) + 
                   (contactResult.score * contactWeight) + 
                   (complianceResult.score * complianceWeight);

      return {
        score: Math.max(0, Math.min(1, score)),
        metrics: this.metrics,
        warnings: this.warnings,
        errors: this.errors
      };

    } catch (error) {
      this.addError(`Compliance metrics collection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return {
        score: 0,
        metrics: this.metrics,
        warnings: this.warnings,
        errors: this.errors
      };
    }
  }
}
