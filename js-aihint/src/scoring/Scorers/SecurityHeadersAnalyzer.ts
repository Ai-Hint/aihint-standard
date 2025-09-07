import { BaseScorer, ScorerResult } from './BaseScorer';
import { MetricStatus } from '../Metrics/MetricResult';

export class SecurityHeadersAnalyzer extends BaseScorer {
  async score(url: string): Promise<ScorerResult> {
    this.metrics = [];
    this.warnings = [];
    this.errors = [];

    const startTime = Date.now();

    try {
      const response = await this.makeRequest(url, { method: 'HEAD' });
      
      if (!response) {
        this.addError('Failed to fetch headers');
        return this.getResult();
      }

      const headers = response.headers;
      let totalScore = 0;
      let checkedHeaders = 0;

      // Check Content Security Policy
      const cspScore = this.checkCSP(headers);
      this.addMetric('csp_header', cspScore.score, cspScore.status, cspScore.message, Date.now() - startTime, cspScore.details);
      totalScore += cspScore.score;
      checkedHeaders++;

      // Check X-Frame-Options
      const frameOptionsScore = this.checkXFrameOptions(headers);
      this.addMetric('x_frame_options', frameOptionsScore.score, frameOptionsScore.status, frameOptionsScore.message, Date.now() - startTime);
      totalScore += frameOptionsScore.score;
      checkedHeaders++;

      // Check X-Content-Type-Options
      const contentTypeScore = this.checkXContentTypeOptions(headers);
      this.addMetric('x_content_type_options', contentTypeScore.score, contentTypeScore.status, contentTypeScore.message, Date.now() - startTime);
      totalScore += contentTypeScore.score;
      checkedHeaders++;

      // Check X-XSS-Protection
      const xssScore = this.checkXXSSProtection(headers);
      this.addMetric('x_xss_protection', xssScore.score, xssScore.status, xssScore.message, Date.now() - startTime);
      totalScore += xssScore.score;
      checkedHeaders++;

      // Check Referrer-Policy
      const referrerScore = this.checkReferrerPolicy(headers);
      this.addMetric('referrer_policy', referrerScore.score, referrerScore.status, referrerScore.message, Date.now() - startTime);
      totalScore += referrerScore.score;
      checkedHeaders++;

      // Check Permissions-Policy
      const permissionsScore = this.checkPermissionsPolicy(headers);
      this.addMetric('permissions_policy', permissionsScore.score, permissionsScore.status, permissionsScore.message, Date.now() - startTime);
      totalScore += permissionsScore.score;
      checkedHeaders++;

      const avgScore = checkedHeaders > 0 ? totalScore / checkedHeaders : 0;
      return this.getResult(avgScore);

    } catch (error) {
      this.addError(`Security headers analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return this.getResult(0);
    }
  }

  private checkCSP(headers: Headers): {score: number, status: MetricStatus, message: string, details?: any} {
    const csp = headers.get('content-security-policy');
    
    if (!csp) {
      return {
        score: 0,
        status: MetricStatus.WARNING,
        message: 'No Content Security Policy header found'
      };
    }

    let score = 0.5; // Base score for having CSP
    const details: any = { directives: [] };

    // Check for important directives
    if (csp.includes('default-src')) {
      score += 0.1;
      details.directives.push('default-src');
    }
    if (csp.includes('script-src')) {
      score += 0.1;
      details.directives.push('script-src');
    }
    if (csp.includes('style-src')) {
      score += 0.1;
      details.directives.push('style-src');
    }
    if (csp.includes('img-src')) {
      score += 0.1;
      details.directives.push('img-src');
    }
    if (csp.includes('object-src')) {
      score += 0.1;
      details.directives.push('object-src');
    }

    // Check for nonce or hash usage (more secure)
    if (csp.includes('nonce-') || csp.includes("'sha256-")) {
      score += 0.1;
      details.usesNonceOrHash = true;
    }

    return {
      score: Math.min(1.0, score),
      status: MetricStatus.SUCCESS,
      message: `CSP header found with ${details.directives.length} directives`,
      details
    };
  }

  private checkXFrameOptions(headers: Headers): {score: number, status: MetricStatus, message: string} {
    const xfo = headers.get('x-frame-options');
    
    if (!xfo) {
      return {
        score: 0,
        status: MetricStatus.WARNING,
        message: 'No X-Frame-Options header found'
      };
    }

    const value = xfo.toLowerCase();
    if (value === 'deny') {
      return {
        score: 1.0,
        status: MetricStatus.SUCCESS,
        message: 'X-Frame-Options set to DENY (most secure)'
      };
    } else if (value.startsWith('sameorigin')) {
      return {
        score: 0.8,
        status: MetricStatus.SUCCESS,
        message: 'X-Frame-Options set to SAMEORIGIN'
      };
    } else if (value.startsWith('allow-from')) {
      return {
        score: 0.6,
        status: MetricStatus.WARNING,
        message: 'X-Frame-Options set to ALLOW-FROM (deprecated)'
      };
    } else {
      return {
        score: 0.4,
        status: MetricStatus.WARNING,
        message: 'X-Frame-Options header present but value unclear'
      };
    }
  }

  private checkXContentTypeOptions(headers: Headers): {score: number, status: MetricStatus, message: string} {
    const xcto = headers.get('x-content-type-options');
    
    if (!xcto) {
      return {
        score: 0,
        status: MetricStatus.WARNING,
        message: 'No X-Content-Type-Options header found'
      };
    }

    if (xcto.toLowerCase() === 'nosniff') {
      return {
        score: 1.0,
        status: MetricStatus.SUCCESS,
        message: 'X-Content-Type-Options set to nosniff'
      };
    } else {
      return {
        score: 0.5,
        status: MetricStatus.WARNING,
        message: 'X-Content-Type-Options header present but not set to nosniff'
      };
    }
  }

  private checkXXSSProtection(headers: Headers): {score: number, status: MetricStatus, message: string} {
    const xxss = headers.get('x-xss-protection');
    
    if (!xxss) {
      return {
        score: 0.3,
        status: MetricStatus.INFO,
        message: 'No X-XSS-Protection header found (modern browsers have built-in XSS protection)'
      };
    }

    if (xxss === '1; mode=block') {
      return {
        score: 0.8,
        status: MetricStatus.SUCCESS,
        message: 'X-XSS-Protection set to 1; mode=block'
      };
    } else if (xxss === '1') {
      return {
        score: 0.6,
        status: MetricStatus.SUCCESS,
        message: 'X-XSS-Protection enabled'
      };
    } else if (xxss === '0') {
      return {
        score: 0.2,
        status: MetricStatus.WARNING,
        message: 'X-XSS-Protection disabled'
      };
    } else {
      return {
        score: 0.4,
        status: MetricStatus.WARNING,
        message: 'X-XSS-Protection header present but value unclear'
      };
    }
  }

  private checkReferrerPolicy(headers: Headers): {score: number, status: MetricStatus, message: string} {
    const referrerPolicy = headers.get('referrer-policy');
    
    if (!referrerPolicy) {
      return {
        score: 0.3,
        status: MetricStatus.INFO,
        message: 'No Referrer-Policy header found'
      };
    }

    const value = referrerPolicy.toLowerCase();
    const securePolicies = ['no-referrer', 'same-origin', 'strict-origin', 'strict-origin-when-cross-origin'];
    
    if (securePolicies.includes(value)) {
      return {
        score: 1.0,
        status: MetricStatus.SUCCESS,
        message: `Referrer-Policy set to ${value} (secure)`
      };
    } else {
      return {
        score: 0.6,
        status: MetricStatus.WARNING,
        message: `Referrer-Policy set to ${value} (less secure)`
      };
    }
  }

  private checkPermissionsPolicy(headers: Headers): {score: number, status: MetricStatus, message: string} {
    const permissionsPolicy = headers.get('permissions-policy');
    
    if (!permissionsPolicy) {
      return {
        score: 0.3,
        status: MetricStatus.INFO,
        message: 'No Permissions-Policy header found'
      };
    }

    // Count restricted features
    const restrictedFeatures = permissionsPolicy.split(',').filter(directive => 
      directive.includes('=()') || directive.includes('=none')
    ).length;

    if (restrictedFeatures >= 5) {
      return {
        score: 1.0,
        status: MetricStatus.SUCCESS,
        message: `Permissions-Policy restricts ${restrictedFeatures} features (excellent)`
      };
    } else if (restrictedFeatures >= 3) {
      return {
        score: 0.7,
        status: MetricStatus.SUCCESS,
        message: `Permissions-Policy restricts ${restrictedFeatures} features (good)`
      };
    } else if (restrictedFeatures >= 1) {
      return {
        score: 0.5,
        status: MetricStatus.WARNING,
        message: `Permissions-Policy restricts ${restrictedFeatures} features (minimal)`
      };
    } else {
      return {
        score: 0.2,
        status: MetricStatus.WARNING,
        message: 'Permissions-Policy present but no features restricted'
      };
    }
  }

  private getResult(score: number = 0): ScorerResult {
    return {
      score: Math.max(0, Math.min(1, score)),
      metrics: this.metrics,
      warnings: this.warnings,
      errors: this.errors
    };
  }
}
