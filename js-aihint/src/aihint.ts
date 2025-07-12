import * as crypto from 'crypto';
import * as fs from 'fs';
import Ajv, { ErrorObject } from 'ajv';
import schema from './schema.json';
import fetch from 'node-fetch';

export interface AiHint {
  version: string;
  type: string;
  target: string;
  issuer: string;
  score: number;
  method: string;
  issued_at: string;
  expires_at: string;
  comment?: string | null;
  public_key_url: string;
  signature?: string | null;
  [key: string]: any;
}

export function canonicalize(obj: object): string {
  return JSON.stringify(obj, Object.keys(obj).sort());
}

export function signHint(hint: AiHint, privateKeyPath: string): AiHint {
  const hintCopy = { ...hint };
  delete hintCopy.signature;
  const canonical = canonicalize(hintCopy);
  const privateKey = fs.readFileSync(privateKeyPath, 'utf8');
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(canonical);
  sign.end();
  const signature = sign.sign(privateKey, 'base64');
  return { ...hint, signature };
}

export async function verifyHint(hint: AiHint, publicKeyPathOrUrl: string): Promise<boolean> {
  const { signature, ...hintCopy } = hint;
  const canonical = canonicalize(hintCopy);
  let publicKey: string;
  if (publicKeyPathOrUrl.startsWith('http://') || publicKeyPathOrUrl.startsWith('https://')) {
    const res = await fetch(publicKeyPathOrUrl);
    publicKey = await res.text();
  } else {
    publicKey = fs.readFileSync(publicKeyPathOrUrl, 'utf8');
  }
  const verify = crypto.createVerify('RSA-SHA256');
  verify.update(canonical);
  verify.end();
  return verify.verify(publicKey, signature || '', 'base64');
}

export function validateHint(hint: AiHint, detailed = false): boolean | ErrorObject[] {
  const ajv = new Ajv();
  const validate = ajv.compile(schema);
  const valid = validate(hint);
  if (detailed && !valid) return validate.errors || [];
  return !!valid;
}

export function generateKeys(outPrivate: string, outPublic: string): void {
  const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  });
  fs.writeFileSync(outPrivate, privateKey);
  fs.writeFileSync(outPublic, publicKey);
} 