#!/usr/bin/env node
import { Command } from 'commander';
import { signHint, verifyHint, validateHint, generateKeys } from './aihint';
import * as fs from 'fs';

const program = new Command();
program
  .name('aihint-js')
  .description('AiHint CLI for signing, verifying, validating, and key generation')
  .version('0.2.0');

program
  .command('sign')
  .description('Sign an AiHint metadata file')
  .requiredOption('-i, --input <file>', 'Input JSON file')
  .requiredOption('-k, --private-key <file>', 'Private key PEM file')
  .requiredOption('-o, --output <file>', 'Output signed JSON file')
  .action((opts) => {
    const hint = JSON.parse(fs.readFileSync(opts.input, 'utf8'));
    const signed = signHint(hint, opts.privateKey);
    fs.writeFileSync(opts.output, JSON.stringify(signed, null, 2));
    console.log('Signed and saved to', opts.output);
  });

program
  .command('verify')
  .description('Verify an AiHint metadata file signature')
  .requiredOption('-i, --input <file>', 'Input signed JSON file')
  .requiredOption('-k, --public-key <file>', 'Public key PEM file or URL')
  .action(async (opts) => {
    const hint = JSON.parse(fs.readFileSync(opts.input, 'utf8'));
    const valid = await verifyHint(hint, opts.publicKey);
    console.log('Signature valid?', valid);
  });

program
  .command('validate')
  .description('Validate an AiHint metadata file against the schema')
  .requiredOption('-i, --input <file>', 'Input JSON file')
  .option('--detailed', 'Show detailed errors')
  .action((opts) => {
    const hint = JSON.parse(fs.readFileSync(opts.input, 'utf8'));
    const result = opts.detailed ? validateHint(hint, true) : validateHint(hint);
    if (opts.detailed && Array.isArray(result)) {
      if (result.length === 0) {
        console.log('Schema valid? true');
      } else {
        console.log('Schema valid? false');
        console.log('Errors:', result);
      }
    } else {
      console.log('Schema valid?', result);
    }
  });

program
  .command('generate-keys')
  .description('Generate an RSA key pair')
  .requiredOption('--out-private <file>', 'Output private key PEM file')
  .requiredOption('--out-public <file>', 'Output public key PEM file')
  .action((opts) => {
    generateKeys(opts.outPrivate, opts.outPublic);
    console.log('Keys generated:', opts.outPrivate, opts.outPublic);
  });

program.parse(process.argv); 