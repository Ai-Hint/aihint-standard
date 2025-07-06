# AIHint API Reference

## Python Library

### Classes
- `AIHint` — Main interface for creating, signing, validating, and verifying hints
- `AIHintGlobal` — Data model for global hints
- `AIHintValidator` — Schema validation
- `AIHintSigner` — Signing utility
- `AIHintVerifier` — Signature verification utility

### Methods
- `AIHint.create_global_hint(...)`
- `AIHint.sign_hint(hint, private_key_path)`
- `AIHint.validate_hint(hint)`
- `AIHint.verify_hint(hint)`
- `AIHint.save_hint(hint, file_path)`
- `AIHint.load_hint(file_path)`

## CLI Commands
- `aihint create` — Create and (optionally) sign a hint
- `aihint validate` — Validate a hint file
- `aihint verify` — Verify a hint's signature
- `aihint info` — Show hint details
- `aihint sign` — Sign an existing hint file

See `README.md` for usage examples. 