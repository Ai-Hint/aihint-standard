"""
AIHint Command Line Interface

CLI tool for creating, validating, and verifying AIHint metadata.
"""

import json
import click
from datetime import datetime, timezone, timedelta
from pathlib import Path
from .core import AIHint, AIHintError, AIHintValidationError, AIHintSignatureError


@click.group()
@click.version_option()
def cli():
    """AIHint - Create, validate, and verify AIHint metadata files."""
    pass


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
            click.echo(json.dumps(hint.dict(), indent=2, default=str))
            
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


if __name__ == '__main__':
    cli() 