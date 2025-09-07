"""
AIHint Command Line Interface

CLI tool for creating, validating, and verifying AIHint metadata.
"""

import json
import click
from datetime import datetime, timezone, timedelta
from pathlib import Path
from .core import AIHint, AIHintError, AIHintValidationError, AIHintSignatureError
from .cli_scoring import scoring
from .scoring import TrustScoringEngine
import asyncio


@click.group()
@click.version_option()
def cli():
    """AIHint - Create, validate, and verify AIHint metadata files."""
    pass


# Add scoring commands
cli.add_command(scoring)


@cli.command()
@click.option('--target', required=True, help='Target domain URL')
@click.option('--issuer', required=True, help='Issuing authority URL')
@click.option('--score', required=True, type=float, help='Trust score (0.0-1.0)')
@click.option('--method', required=True, help='Scoring method used')
@click.option('--public-key-url', required=True, help='Public key URL')
@click.option('--expires-in', default=365, help='Expiration in days (default: 365)')
@click.option('--comment', help='Optional comment')
@click.option('--output', '-o', help='Output file path')
@click.option('--private-key', help='Private key file for signing')
@click.option('--version', default='0.1', help='AIHint version')
def create(target, issuer, score, method, public_key_url, expires_in, comment, output, private_key, version):
    """Create a new AIHint metadata file."""
    try:
        aihint = AIHint()
        
        # Calculate expiration date
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in)
        
        # Create hint
        hint = aihint.create_global_hint(
            target=target,
            issuer=issuer,
            score=score,
            method=method,
            public_key_url=public_key_url,
            expires_at=expires_at,
            comment=comment,
            version=version
        )
        
        # Sign if private key provided
        if private_key:
            if not Path(private_key).exists():
                raise click.ClickException(f"Private key file not found: {private_key}")
            hint = aihint.sign_hint(hint, private_key)
            click.echo("✓ Hint signed successfully")
        
        # Validate
        if aihint.validate_hint(hint):
            click.echo("✓ Hint validation passed")
        else:
            raise click.ClickException("Hint validation failed")
        
        # Output
        if output:
            aihint.save_hint(hint, output)
            click.echo(f"✓ Hint saved to {output}")
        else:
            # Use proper serialization
            data = aihint._serialize_hint(hint)
            click.echo(json.dumps(data, indent=2))
            
    except AIHintError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def validate(file_path):
    """Validate an AIHint metadata file."""
    try:
        aihint = AIHint()
        
        # Load and validate
        hint = aihint.load_hint(file_path)
        
        if aihint.validate_hint(hint):
            click.echo("✓ Validation passed")
            
            # Check expiration
            now = datetime.now(timezone.utc)
            if hint.expires_at < now:
                click.echo("⚠ Warning: Hint has expired")
            else:
                days_left = (hint.expires_at - now).days
                click.echo(f"✓ Valid for {days_left} more days")
        else:
            raise click.ClickException("Validation failed")
            
    except AIHintError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def verify(file_path):
    """Verify an AIHint metadata file signature."""
    try:
        aihint = AIHint()
        
        # Load and verify
        hint = aihint.load_hint(file_path)
        
        if aihint.verify_hint(hint):
            click.echo("✓ Signature verification passed")
        else:
            raise click.ClickException("Signature verification failed")
            
    except AIHintError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def info(file_path):
    """Display information about an AIHint metadata file."""
    try:
        aihint = AIHint()
        hint = aihint.load_hint(file_path)
        
        click.echo("AIHint Information:")
        click.echo(f"  Version: {hint.version}")
        click.echo(f"  Type: {hint.type}")
        click.echo(f"  Target: {hint.target}")
        click.echo(f"  Issuer: {hint.issuer}")
        click.echo(f"  Score: {hint.score}")
        click.echo(f"  Method: {hint.method}")
        click.echo(f"  Issued: {hint.issued_at}")
        click.echo(f"  Expires: {hint.expires_at}")
        if hint.comment:
            click.echo(f"  Comment: {hint.comment}")
        
        # Check status
        now = datetime.now(timezone.utc)
        if hint.expires_at < now:
            click.echo("  Status: EXPIRED")
        else:
            days_left = (hint.expires_at - now).days
            click.echo(f"  Status: Valid ({days_left} days left)")
            
    except AIHintError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--private-key', required=True, help='Private key file for signing')
def sign(file_path, private_key):
    """Sign an existing AIHint metadata file."""
    try:
        aihint = AIHint()
        
        # Load hint
        hint = aihint.load_hint(file_path)
        
        # Sign
        signed_hint = aihint.sign_hint(hint, private_key)
        
        # Save back to file
        aihint.save_hint(signed_hint, file_path)
        
        click.echo("✓ File signed successfully")
        
    except AIHintError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.option('--target', required=True, help='Target domain URL to score and create AiHint for')
@click.option('--issuer', required=True, help='Issuing authority URL')
@click.option('--public-key-url', required=True, help='Public key URL')
@click.option('--expires-in', default=365, help='Expiration in days (default: 365)')
@click.option('--comment', help='Optional comment')
@click.option('--output', '-o', help='Output file path')
@click.option('--private-key', help='Private key file for signing')
@click.option('--version', default='0.1', help='AIHint version')
@click.option('--config', '-c', help='Scoring configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def create_with_score(target, issuer, public_key_url, expires_in, comment, output, private_key, version, config, verbose):
    """Create an AIHint metadata file with automated trust scoring."""
    try:
        # Load scoring configuration
        scoring_config = {}
        if config:
            try:
                with open(config, 'r') as f:
                    scoring_config = json.load(f)
            except Exception as e:
                raise click.ClickException(f"Error loading config: {e}")
        
        # Initialize scoring engine
        if verbose:
            click.echo("🔍 Initializing trust scoring engine...")
        engine = TrustScoringEngine(scoring_config)
        
        # Score the website
        if verbose:
            click.echo(f"📊 Scoring website: {target}")
        
        # Run the scoring asynchronously
        result = asyncio.run(engine.score_website(target))
        
        if verbose:
            click.echo(f"✅ Scoring completed:")
            click.echo(f"   Trust Score: {result.final_score:.3f}")
            click.echo(f"   Trust Level: {result.trust_level.name}")
            click.echo(f"   Confidence: {result.confidence:.3f}")
            click.echo(f"   Security: {result.security_score:.3f}")
            click.echo(f"   Reputation: {result.reputation_score:.3f}")
            click.echo(f"   Compliance: {result.compliance_score:.3f}")
        
        # Create AiHint with the scored trust value
        aihint = AIHint()
        
        # Calculate expiration date
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in)
        
        # Create hint with the scored trust value
        hint = aihint.create_global_hint(
            target=target,
            issuer=issuer,
            score=result.final_score,  # Use the scored trust value
            method="aihint-scoring-v1",  # Use our scoring method
            public_key_url=public_key_url,
            expires_at=expires_at,
            comment=comment or f"Auto-scored with {result.trust_level.name} trust level",
            version=version
        )
        
        # Sign if private key provided
        if private_key:
            if not Path(private_key).exists():
                raise click.ClickException(f"Private key file not found: {private_key}")
            hint = aihint.sign_hint(hint, private_key)
            click.echo("✓ Hint signed successfully")
        
        # Validate
        if aihint.validate_hint(hint):
            click.echo("✓ Hint validation passed")
        else:
            raise click.ClickException("Hint validation failed")
        
        # Output
        if output:
            aihint.save_hint(hint, output)
            click.echo(f"✓ AiHint saved to {output}")
            click.echo(f"📊 Trust Score: {result.final_score:.3f} ({result.trust_level.name})")
        else:
            # Use proper serialization
            data = aihint._serialize_hint(hint)
            click.echo(json.dumps(data, indent=2))
            
    except AIHintError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Scoring or creation failed: {e}")


if __name__ == '__main__':
    cli() 