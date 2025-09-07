import { BaseScorer, ScorerResult } from './BaseScorer';
import { MetricStatus } from '../Metrics/MetricResult';
import * as https from 'https';
import * as tls from 'tls';

export class SSLTLSValidator extends BaseScorer {
  async score(url: string): Promise<ScorerResult> {
    this.metrics = [];
    this.warnings = [];
    this.errors = [];

    const startTime = Date.now();
    const domain = this.getDomain(url);

    try {
      // Check if URL uses HTTPS
      if (!url.startsWith('https://')) {
        this.addMetric('https_check', 0, MetricStatus.ERROR, 'Site does not use HTTPS', Date.now() - startTime);
        return this.getResult();
      }

      // Check SSL certificate
      const certResult = await this.checkSSLCertificate(domain);
      this.addMetric('ssl_certificate', certResult.score, certResult.status, certResult.message, certResult.executionTime, certResult.details);

      // Check TLS version
      const tlsResult = await this.checkTLSVersion(domain);
      this.addMetric('tls_version', tlsResult.score, tlsResult.status, tlsResult.message, tlsResult.executionTime);

      // Check HSTS header
      const hstsResult = await this.checkHSTS(url);
      this.addMetric('hsts_header', hstsResult.score, hstsResult.status, hstsResult.message, hstsResult.executionTime);

      // Calculate overall score
      const scores = this.metrics.map(m => m.score);
      const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;

      return this.getResult(avgScore);

    } catch (error) {
      this.addError(`SSL/TLS validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return this.getResult(0);
    }
  }

  private async checkSSLCertificate(domain: string): Promise<{score: number, status: MetricStatus, message: string, executionTime: number, details?: any}> {
    const startTime = Date.now();
    
    return new Promise((resolve) => {
      const socket = tls.connect(443, domain, { rejectUnauthorized: false }, () => {
        const cert = socket.getPeerCertificate();
        const executionTime = Date.now() - startTime;
        
        if (!cert || !cert.valid_to) {
          resolve({
            score: 0,
            status: MetricStatus.ERROR,
            message: 'No valid SSL certificate found',
            executionTime
          });
          return;
        }

        const now = new Date();
        const validTo = new Date(cert.valid_to);
        const daysUntilExpiry = Math.floor((validTo.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

        let score = 0.5; // Base score for having a certificate
        let status = MetricStatus.SUCCESS;
        let message = 'Valid SSL certificate found';

        if (daysUntilExpiry < 0) {
          score = 0;
          status = MetricStatus.ERROR;
          message = 'SSL certificate has expired';
        } else if (daysUntilExpiry < 30) {
          score = 0.3;
          status = MetricStatus.WARNING;
          message = `SSL certificate expires in ${daysUntilExpiry} days`;
        } else if (daysUntilExpiry < 90) {
          score = 0.7;
          status = MetricStatus.WARNING;
          message = `SSL certificate expires in ${daysUntilExpiry} days`;
        } else {
          score = 1.0;
          message = `SSL certificate valid for ${daysUntilExpiry} days`;
        }

        resolve({
          score,
          status,
          message,
          executionTime,
          details: {
            issuer: cert.issuer?.CN || 'Unknown',
            validFrom: cert.valid_from,
            validTo: cert.valid_to,
            daysUntilExpiry
          }
        });
      });

      socket.on('error', () => {
        resolve({
          score: 0,
          status: MetricStatus.ERROR,
          message: 'Failed to connect to SSL certificate',
          executionTime: Date.now() - startTime
        });
      });

      socket.setTimeout(this.config.timeouts.ssl, () => {
        socket.destroy();
        resolve({
          score: 0,
          status: MetricStatus.ERROR,
          message: 'SSL certificate check timeout',
          executionTime: Date.now() - startTime
        });
      });
    });
  }

  private async checkTLSVersion(domain: string): Promise<{score: number, status: MetricStatus, message: string, executionTime: number}> {
    const startTime = Date.now();
    
    return new Promise((resolve) => {
      const socket = tls.connect(443, domain, { rejectUnauthorized: false }, () => {
        const protocol = socket.getProtocol();
        const executionTime = Date.now() - startTime;
        
        let score = 0;
        let status = MetricStatus.ERROR;
        let message = 'Unknown TLS version';

        if (protocol === 'TLSv1.3') {
          score = 1.0;
          status = MetricStatus.SUCCESS;
          message = 'Using TLS 1.3 (most secure)';
        } else if (protocol === 'TLSv1.2') {
          score = 0.8;
          status = MetricStatus.SUCCESS;
          message = 'Using TLS 1.2 (secure)';
        } else if (protocol === 'TLSv1.1') {
          score = 0.4;
          status = MetricStatus.WARNING;
          message = 'Using TLS 1.1 (deprecated)';
        } else if (protocol === 'TLSv1') {
          score = 0.2;
          status = MetricStatus.WARNING;
          message = 'Using TLS 1.0 (deprecated and insecure)';
        } else {
          score = 0;
          status = MetricStatus.ERROR;
          message = 'Using insecure or unknown TLS version';
        }

        resolve({ score, status, message, executionTime });
      });

      socket.on('error', () => {
        resolve({
          score: 0,
          status: MetricStatus.ERROR,
          message: 'Failed to check TLS version',
          executionTime: Date.now() - startTime
        });
      });

      socket.setTimeout(this.config.timeouts.ssl, () => {
        socket.destroy();
        resolve({
          score: 0,
          status: MetricStatus.ERROR,
          message: 'TLS version check timeout',
          executionTime: Date.now() - startTime
        });
      });
    });
  }

  private async checkHSTS(url: string): Promise<{score: number, status: MetricStatus, message: string, executionTime: number}> {
    const startTime = Date.now();
    
    try {
      const response = await this.makeRequest(url, { method: 'HEAD' });
      const executionTime = Date.now() - startTime;
      
      if (!response) {
        return {
          score: 0,
          status: MetricStatus.ERROR,
          message: 'Failed to check HSTS header',
          executionTime
        };
      }

      const hstsHeader = response.headers.get('strict-transport-security');
      
      if (!hstsHeader) {
        return {
          score: 0.3,
          status: MetricStatus.WARNING,
          message: 'No HSTS header found',
          executionTime
        };
      }

      // Parse HSTS header
      const maxAgeMatch = hstsHeader.match(/max-age=(\d+)/);
      const maxAge = maxAgeMatch ? parseInt(maxAgeMatch[1]) : 0;
      const includesSubDomains = hstsHeader.includes('includeSubDomains');
      const preload = hstsHeader.includes('preload');

      let score = 0.5; // Base score for having HSTS
      let message = 'HSTS header found';

      if (maxAge >= 31536000) { // 1 year
        score += 0.3;
        message += ` with long max-age (${maxAge}s)`;
      } else if (maxAge >= 86400) { // 1 day
        score += 0.1;
        message += ` with moderate max-age (${maxAge}s)`;
      }

      if (includesSubDomains) {
        score += 0.1;
        message += ', includes subdomains';
      }

      if (preload) {
        score += 0.1;
        message += ', preload enabled';
      }

      return {
        score: Math.min(1.0, score),
        status: MetricStatus.SUCCESS,
        message,
        executionTime
      };

    } catch (error) {
      return {
        score: 0,
        status: MetricStatus.ERROR,
        message: `HSTS check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        executionTime: Date.now() - startTime
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
