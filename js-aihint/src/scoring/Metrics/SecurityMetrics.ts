import { BaseMetrics } from './BaseMetrics';
import { MetricResult, MetricStatus } from './MetricResult';
import { SSLTLSValidator } from '../Scorers/SSLTLSValidator';
import { SecurityHeadersAnalyzer } from '../Scorers/SecurityHeadersAnalyzer';
import { MalwareChecker } from '../Scorers/MalwareChecker';

export class SecurityMetrics extends BaseMetrics {
  private sslValidator: SSLTLSValidator;
  private headersAnalyzer: SecurityHeadersAnalyzer;
  private malwareChecker: MalwareChecker;

  constructor(config: any) {
    super(config);
    this.sslValidator = new SSLTLSValidator(config);
    this.headersAnalyzer = new SecurityHeadersAnalyzer(config);
    this.malwareChecker = new MalwareChecker(config);
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
      // Run security checks in parallel
      const [sslResult, headersResult, malwareResult] = await Promise.all([
        this.sslValidator.score(url),
        this.headersAnalyzer.score(url),
        this.malwareChecker.score(url)
      ]);

      // Add all metrics
      this.metrics.push(...sslResult.metrics);
      this.metrics.push(...headersResult.metrics);
      this.metrics.push(...malwareResult.metrics);

      // Add warnings and errors
      this.warnings.push(...sslResult.warnings);
      this.warnings.push(...headersResult.warnings);
      this.warnings.push(...malwareResult.warnings);

      this.errors.push(...sslResult.errors);
      this.errors.push(...headersResult.errors);
      this.errors.push(...malwareResult.errors);

      // Calculate weighted score
      const sslWeight = 0.4;
      const headersWeight = 0.35;
      const malwareWeight = 0.25;

      const score = (sslResult.score * sslWeight) + 
                   (headersResult.score * headersWeight) + 
                   (malwareResult.score * malwareWeight);

      return {
        score: Math.max(0, Math.min(1, score)),
        metrics: this.metrics,
        warnings: this.warnings,
        errors: this.errors
      };

    } catch (error) {
      this.addError(`Security metrics collection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return {
        score: 0,
        metrics: this.metrics,
        warnings: this.warnings,
        errors: this.errors
      };
    }
  }
}
