#!/usr/bin/env node

import { Command } from 'commander';
import { TrustScoringEngine } from './TrustScoringEngine';
import { TrustLevelHelper } from './TrustLevel';
import * as fs from 'fs';
import * as path from 'path';

const program = new Command();

program
  .name('aihint-scoring')
  .description('AiHint Trust Scoring CLI')
  .version('1.0.0');

program
  .command('score')
  .description('Score a single URL')
  .argument('<url>', 'URL to score')
  .option('-v, --verbose', 'Verbose output')
  .option('-o, --output <file>', 'Output file for JSON results')
  .action(async (url: string, options: any) => {
    try {
      const scoringEngine = new TrustScoringEngine();
      const result = await scoringEngine.scoreWebsite(url);

      if (options.verbose) {
        console.log(`URL: ${result.url}`);
        console.log(`Trust Score: ${result.finalScore.toFixed(3)}`);
        console.log(`Trust Level: ${result.trustLevel} (${TrustLevelHelper.getDescription(result.trustLevel)})`);
        console.log(`Confidence: ${result.confidence.toFixed(3)}`);
        console.log(`Security Score: ${result.securityScore.toFixed(3)}`);
        console.log(`Reputation Score: ${result.reputationScore.toFixed(3)}`);
        console.log(`Compliance Score: ${result.complianceScore.toFixed(3)}`);
        
        if (result.warnings.length > 0) {
          console.log('\nWarnings:');
          result.warnings.forEach(warning => console.log(`  - ${warning}`));
        }
        
        if (result.errors.length > 0) {
          console.log('\nErrors:');
          result.errors.forEach(error => console.log(`  - ${error}`));
        }
      } else {
        console.log(`URL: ${result.url}`);
        console.log(`Trust Score: ${result.finalScore.toFixed(3)}`);
        console.log(`Trust Level: ${result.trustLevel} (${TrustLevelHelper.getDescription(result.trustLevel)})`);
        console.log(`Confidence: ${result.confidence.toFixed(3)}`);
      }

      if (options.output) {
        fs.writeFileSync(options.output, JSON.stringify(result.toJSON(), null, 2));
        console.log(`\nResults saved to: ${options.output}`);
      }
    } catch (error) {
      console.error(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      process.exit(1);
    }
  });

program
  .command('batch')
  .description('Score multiple URLs')
  .option('-u, --urls <urls>', 'Comma-separated list of URLs')
  .option('-f, --file <file>', 'File containing URLs (one per line)')
  .option('-o, --output <file>', 'Output file for JSON results')
  .action(async (options: any) => {
    try {
      let urls: string[] = [];

      if (options.urls) {
        urls = options.urls.split(',').map((url: string) => url.trim());
      } else if (options.file) {
        const content = fs.readFileSync(options.file, 'utf8');
        urls = content.split('\n').map((url: string) => url.trim()).filter((url: string) => url.length > 0);
      } else {
        console.error('Error: Either --urls or --file must be specified');
        process.exit(1);
      }

      const scoringEngine = new TrustScoringEngine();
      const results = [];

      for (const url of urls) {
        console.log(`Scoring: ${url}`);
        const result = await scoringEngine.scoreWebsite(url);
        results.push(result.toJSON());
      }

      if (options.output) {
        fs.writeFileSync(options.output, JSON.stringify(results, null, 2));
        console.log(`\nResults saved to: ${options.output}`);
      } else {
        console.log('\nBatch Results:');
        results.forEach(result => {
          console.log(`${result.url.padEnd(30)} | Score: ${result.final_score.toFixed(3)} | Level: ${result.trust_level.padEnd(10)} | Confidence: ${result.confidence.toFixed(3)}`);
        });
      }
    } catch (error) {
      console.error(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      process.exit(1);
    }
  });

program
  .command('config')
  .description('Generate sample configuration file')
  .option('-o, --output <file>', 'Output file for configuration')
  .action((options: any) => {
    const config = {
      timeouts: {
        http: 10000,
        dns: 5000,
        ssl: 5000
      },
      apiKeys: {
        googleSafeBrowsing: 'YOUR_GOOGLE_SAFE_BROWSING_API_KEY',
        virusTotal: 'YOUR_VIRUSTOTAL_API_KEY',
        phishTank: 'YOUR_PHISHTANK_API_KEY'
      },
      weights: {
        security: 0.4,
        reputation: 0.35,
        compliance: 0.25
      }
    };

    const outputFile = options.output || 'scoring-config.json';
    fs.writeFileSync(outputFile, JSON.stringify(config, null, 2));
    console.log(`Configuration saved to: ${outputFile}`);
  });

program.parse();
