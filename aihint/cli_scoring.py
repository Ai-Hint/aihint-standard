"""
AiHint Trust Scoring CLI

Command-line interface for the trust scoring system.
"""

import asyncio
import json
import click
from datetime import datetime, timezone
from .scoring import TrustScoringEngine


@click.group()
def scoring():
    """AiHint Trust Scoring System - Score website trustworthiness."""
    pass


@scoring.command()
@click.argument('url')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text', 'table']), default='text', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def score(url, config, output, output_format, verbose):
    """Score a single website's trustworthiness."""
    
    # Load configuration
    scoring_config = {}
    if config:
        try:
            with open(config, 'r') as f:
                scoring_config = json.load(f)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            return
    
    # Initialize scoring engine
    engine = TrustScoringEngine(scoring_config)
    
    # Score the website
    click.echo(f"Scoring: {url}")
    try:
        result = asyncio.run(engine.score_website(url))
        
        if output_format == 'json':
            output_data = {
                'url': result.url,
                'final_score': result.final_score,
                'trust_level': result.trust_level.name,
                'confidence': result.confidence,
                'security_score': result.security_score,
                'reputation_score': result.reputation_score,
                'compliance_score': result.compliance_score,
                'warnings': result.warnings,
                'errors': result.errors,
                'timestamp': result.timestamp.isoformat(),
                'method': result.method,
                'detailed_metrics': result.detailed_metrics
            }
            
            output_text = json.dumps(output_data, indent=2)
        elif output_format == 'table':
            output_text = _format_table_output(result)
        else:  # text
            output_text = _format_text_output(result, verbose)
        
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            click.echo(f"Results saved to: {output}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"Error scoring website: {e}", err=True)


@scoring.command()
@click.argument('urls', nargs=-1)
@click.option('--file', '-f', help='File containing URLs (one per line)')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text', 'table']), default='text', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch(urls, file, config, output, output_format, verbose):
    """Score multiple websites in batch."""
    
    # Collect URLs
    all_urls = list(urls)
    if file:
        try:
            with open(file, 'r') as f:
                file_urls = [line.strip() for line in f if line.strip()]
                all_urls.extend(file_urls)
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            return
    
    if not all_urls:
        click.echo("No URLs provided", err=True)
        return
    
    # Load configuration
    scoring_config = {}
    if config:
        try:
            with open(config, 'r') as f:
                scoring_config = json.load(f)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            return
    
    # Initialize scoring engine
    engine = TrustScoringEngine(scoring_config)
    
    # Score all websites
    click.echo(f"Scoring {len(all_urls)} websites...")
    results = []
    
    for i, url in enumerate(all_urls, 1):
        click.echo(f"[{i}/{len(all_urls)}] Scoring: {url}")
        try:
            result = asyncio.run(engine.score_website(url))
            results.append(result)
        except Exception as e:
            click.echo(f"  Error: {e}")
            continue
    
    if not results:
        click.echo("No successful scores", err=True)
        return
    
    # Format output
    if output_format == 'json':
        output_data = []
        for result in results:
            output_data.append({
                'url': result.url,
                'final_score': result.final_score,
                'trust_level': result.trust_level.name,
                'confidence': result.confidence,
                'security_score': result.security_score,
                'reputation_score': result.reputation_score,
                'compliance_score': result.compliance_score,
                'warnings': result.warnings,
                'errors': result.errors,
                'timestamp': result.timestamp.isoformat(),
                'method': result.method,
                'detailed_metrics': result.detailed_metrics
            })
        
        output_text = json.dumps(output_data, indent=2)
    elif output_format == 'table':
        output_text = _format_batch_table_output(results)
    else:  # text
        output_text = _format_batch_text_output(results, verbose)
    
    if output:
        with open(output, 'w') as f:
            f.write(output_text)
        click.echo(f"Results saved to: {output}")
    else:
        click.echo(output_text)


@scoring.command()
@click.option('--output', '-o', help='Output file path')
def config(output):
    """Generate a sample configuration file."""
    
    sample_config = {
        "ssl": {
            "timeout": 10
        },
        "headers": {
            "timeout": 10
        },
        "malware": {
            "timeout": 10,
            "google_safe_browsing": {
                "enabled": False,
                "api_key": "YOUR_API_KEY_HERE"
            },
            "virustotal": {
                "enabled": False,
                "api_key": "YOUR_API_KEY_HERE"
            },
            "phishtank": {
                "enabled": False
            }
        },
        "reputation": {
            "timeout": 10
        },
        "domain_age": {
            "timeout": 10
        },
        "incidents": {
            "timeout": 10
        },
        "privacy": {
            "timeout": 10
        },
        "contact": {
            "timeout": 10
        },
        "compliance": {
            "timeout": 10
        }
    }
    
    config_text = json.dumps(sample_config, indent=2)
    
    if output:
        with open(output, 'w') as f:
            f.write(config_text)
        click.echo(f"Sample configuration saved to: {output}")
    else:
        click.echo(config_text)


def _format_text_output(result, verbose=False):
    """Format single result as text."""
    output = []
    output.append(f"Trust Score: {result.final_score:.3f}")
    output.append(f"Trust Level: {result.trust_level.name}")
    output.append(f"Confidence: {result.confidence:.3f}")
    output.append("")
    output.append("Component Scores:")
    output.append(f"  Security: {result.security_score:.3f}")
    output.append(f"  Reputation: {result.reputation_score:.3f}")
    output.append(f"  Compliance: {result.compliance_score:.3f}")
    
    if result.warnings:
        output.append("")
        output.append("Warnings:")
        for warning in result.warnings:
            output.append(f"  - {warning}")
    
    if result.errors:
        output.append("")
        output.append("Errors:")
        for error in result.errors:
            output.append(f"  - {error}")
    
    if verbose:
        output.append("")
        output.append("Detailed Metrics:")
        output.append(json.dumps(result.detailed_metrics, indent=2))
    
    return "\n".join(output)


def _format_table_output(result):
    """Format single result as table."""
    output = []
    output.append("┌─────────────────┬─────────────────────────────────────────┐")
    output.append("│ Metric          │ Value                                   │")
    output.append("├─────────────────┼─────────────────────────────────────────┤")
    output.append(f"│ Final Score     │ {result.final_score:.3f}                                    │")
    output.append(f"│ Trust Level     │ {result.trust_level.name:<39} │")
    output.append(f"│ Confidence      │ {result.confidence:.3f}                                    │")
    output.append(f"│ Security Score  │ {result.security_score:.3f}                                    │")
    output.append(f"│ Reputation      │ {result.reputation_score:.3f}                                    │")
    output.append(f"│ Compliance      │ {result.compliance_score:.3f}                                    │")
    output.append("└─────────────────┴─────────────────────────────────────────┘")
    
    return "\n".join(output)


def _format_batch_text_output(results, verbose=False):
    """Format batch results as text."""
    output = []
    output.append(f"Batch Scoring Results ({len(results)} websites)")
    output.append("=" * 50)
    
    for result in results:
        output.append(f"\n{result.url}")
        output.append(f"  Score: {result.final_score:.3f} ({result.trust_level.name})")
        output.append(f"  Security: {result.security_score:.3f}, Reputation: {result.reputation_score:.3f}, Compliance: {result.compliance_score:.3f}")
        
        if result.warnings:
            output.append(f"  Warnings: {', '.join(result.warnings)}")
        
        if result.errors:
            output.append(f"  Errors: {', '.join(result.errors)}")
    
    # Summary
    if results:
        avg_score = sum(r.final_score for r in results) / len(results)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        output.append("\nSummary:")
        output.append(f"  Average Score: {avg_score:.3f}")
        output.append(f"  Average Confidence: {avg_confidence:.3f}")
        
        # Trust level distribution
        trust_levels = {}
        for result in results:
            level = result.trust_level.name
            trust_levels[level] = trust_levels.get(level, 0) + 1
        
        output.append("  Trust Level Distribution:")
        for level, count in trust_levels.items():
            output.append(f"    {level}: {count}")
    
    return "\n".join(output)


def _format_batch_table_output(results):
    """Format batch results as table."""
    output = []
    output.append("┌─────────────────────────────────┬──────────┬─────────────┬──────────┬─────────────┬─────────────┐")
    output.append("│ URL                             │ Score    │ Trust Level │ Security │ Reputation  │ Compliance  │")
    output.append("├─────────────────────────────────┼──────────┼─────────────┼──────────┼─────────────┼─────────────┤")
    
    for result in results:
        url = result.url[:30] + "..." if len(result.url) > 30 else result.url
        output.append(f"│ {url:<31} │ {result.final_score:6.3f}  │ {result.trust_level.name:<11} │ {result.security_score:6.3f}  │ {result.reputation_score:9.3f}  │ {result.compliance_score:9.3f}  │")
    
    output.append("└─────────────────────────────────┴──────────┴─────────────┴──────────┴─────────────┴─────────────┘")
    
    return "\n".join(output)


if __name__ == '__main__':
    scoring()
