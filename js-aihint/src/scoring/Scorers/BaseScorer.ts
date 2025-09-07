import { MetricResult, MetricStatus } from '../Metrics/MetricResult';
import { ScoringConfig } from '../TrustScoringEngine';

export interface ScorerResult {
  score: number;
  metrics: MetricResult[];
  warnings: string[];
  errors: string[];
}

export abstract class BaseScorer {
  protected config: ScoringConfig;
  protected metrics: MetricResult[] = [];
  protected warnings: string[] = [];
  protected errors: string[] = [];

  constructor(config: ScoringConfig) {
    this.config = config;
  }

  protected addMetric(name: string, score: number, status: MetricStatus, message: string, executionTime: number, details?: any): void {
    this.metrics.push(new MetricResult({
      name,
      score,
      status,
      message,
      executionTime,
      details
    }));
  }

  protected addWarning(message: string): void {
    this.warnings.push(message);
  }

  protected addError(message: string): void {
    this.errors.push(message);
  }

  protected async makeRequest(url: string, options: RequestInit = {}): Promise<Response | null> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeouts.http);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'User-Agent': 'AiHint-Scoring/1.0',
          ...options.headers
        }
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        this.addWarning(`Request timeout for ${url}`);
      } else {
        this.addWarning(`Request failed for ${url}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
      return null;
    }
  }

  protected getDomain(url: string): string {
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  }

  public abstract score(url: string): Promise<ScorerResult>;
}
