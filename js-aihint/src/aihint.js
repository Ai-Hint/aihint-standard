const crypto = require('crypto');
const fs = require('fs');
const Ajv = require('ajv');
const schema = require('./schema.json');

// Canonical JSON (sorted keys)
function canonicalize(obj) {
  return JSON.stringify(obj, Object.keys(obj).sort());
}

// Sign AiHint metadata
function signHint(hint, privateKeyPath) {
  const hintCopy = { ...hint };
  delete hintCopy.signature;
  const canonical = canonicalize(hintCopy);
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(canonical);
  sign.end();
  const privateKey = fs.readFileSync(privateKeyPath, 'utf8');
  const signature = sign.sign(privateKey, 'base64');
  return { ...hint, signature };
}

// Verify AiHint signature
function verifyHint(hint, publicKeyPath) {
  const { signature, ...hintCopy } = hint;
  const canonical = canonicalize(hintCopy);
  const verify = crypto.createVerify('RSA-SHA256');
  verify.update(canonical);
  verify.end();
  const publicKey = fs.readFileSync(publicKeyPath, 'utf8');
  return verify.verify(publicKey, signature, 'base64');
}

// Validate AiHint metadata
function validateHint(hint) {
  const ajv = new Ajv();
  const validate = ajv.compile(schema);
  return validate(hint);
}

module.exports = { signHint, verifyHint, validateHint }; 