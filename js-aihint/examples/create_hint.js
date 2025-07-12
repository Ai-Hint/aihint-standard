const { signHint, verifyHint, validateHint } = require('../src/aihint');
const fs = require('fs');

const hint = {
  version: "0.1",
  type: "global",
  target: "https://example.com",
  issuer: "https://trust.aihint.org",
  score: 0.92,
  method: "aihint-core-v1",
  issued_at: "2025-01-01T12:00:00Z",
  expires_at: "2026-01-01T00:00:00Z",
  comment: "Example AiHint for demonstration",
  public_key_url: "https://trust.aihint.org/pubkey.pem"
};

const signed = signHint(hint, 'private_key.pem');
fs.writeFileSync('aihint.json', JSON.stringify(signed, null, 2));
console.log('Signed:', signed);

const valid = verifyHint(signed, 'public_key.pem');
console.log('Signature valid?', valid);

const schemaValid = validateHint(signed);
console.log('Schema valid?', schemaValid); 