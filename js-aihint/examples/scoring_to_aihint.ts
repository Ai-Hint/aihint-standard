import { signHint, verifyHint, validateHint, AiHint } from '../src/aihint';
import { TrustScoringEngine } from '../src/scoring/TrustScoringEngine';
import { TrustLevelHelper } from '../src/scoring/TrustLevel';
import * as fs from 'fs';

async function main() {
  console.log('=== AiHint Generation with Trust Scoring (TypeScript) ===\n');

  // Initialize the trust scoring engine
  const scoringEngine = new TrustScoringEngine();

  // URLs to score and create AiHints for
  const urls = [
    'https://github.com',
    'https://stackoverflow.com',
    'https://example.com'
  ];

  for (const url of urls) {
    console.log(`Processing: ${url}`);
    console.log('-'.repeat(50));

    try {
      // Get trust score
      const result = await scoringEngine.scoreWebsite(url);

      // Create AiHint data structure
      const aihintData: AiHint = {
        version: '0.1',
        type: 'global',
        target: url,
        issuer: 'https://trust.aihint.org',
        score: result.finalScore,
        method: 'aihint-scoring-v1', // Use scoring method
        issued_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year
        comment: `Trust score: ${result.finalScore.toFixed(3)} (Level: ${result.trustLevel})`,
        public_key_url: 'https://trust.aihint.org/pubkey.pem'
      };

      // Validate the AiHint
      const isValid = validateHint(aihintData);
      console.log(`AiHint valid: ${isValid ? 'YES' : 'NO'}`);

      // Display the results
      console.log(`Score: ${result.finalScore.toFixed(3)}`);
      console.log(`Trust Level: ${result.trustLevel} (${TrustLevelHelper.getDescription(result.trustLevel)})`);
      console.log(`Security Score: ${result.securityScore.toFixed(3)}`);
      console.log(`Reputation Score: ${result.reputationScore.toFixed(3)}`);
      console.log(`Compliance Score: ${result.complianceScore.toFixed(3)}`);

      // Save to file
      const filename = `aihint_${new URL(url).hostname}.json`;
      fs.writeFileSync(filename, JSON.stringify(aihintData, null, 2));
      console.log(`Saved to: ${filename}`);

      // Display JSON structure
      console.log('\nAiHint JSON:');
      console.log(JSON.stringify(aihintData, null, 2));

    } catch (error) {
      console.log(`Error processing ${url}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }

    console.log('\n' + '='.repeat(70) + '\n');
  }

  console.log('Done! Generated AiHint files for all URLs.');
}

main().catch(console.error);
