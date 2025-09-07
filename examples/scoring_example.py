#!/usr/bin/env python3
"""
AiHint Trust Scoring Example

Demonstrates the complete trust scoring system with all three phases:
- Phase 1: Core Security Metrics (SSL, headers, malware)
- Phase 2: Reputation Signals (domain age, incidents, reputation)
- Phase 3: Content & Compliance (privacy, contact, legal)
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone

# Add the parent directory to the path so we can import aihint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aihint.scoring import TrustScoringEngine


async def main():
    """Main example function."""
    print("AiHint Trust Scoring System Example")
    print("=" * 50)
    
    # Configuration for the scoring engine
    config = {
        'ssl': {
            'timeout': 10
        },
        'headers': {
            'timeout': 10
        },
        'malware': {
            'timeout': 10,
            'google_safe_browsing': {
                'enabled': False,  # Set to True and add API key for real checks
                'api_key': None
            },
            'virustotal': {
                'enabled': False,  # Set to True and add API key for real checks
                'api_key': None
            },
            'phishtank': {
                'enabled': False  # Set to True for real checks
            }
        },
        'reputation': {
            'timeout': 10
        },
        'domain_age': {
            'timeout': 10
        },
        'incidents': {
            'timeout': 10
        },
        'privacy': {
            'timeout': 10
        },
        'contact': {
            'timeout': 10
        },
        'compliance': {
            'timeout': 10
        }
    }
    
    # Initialize the scoring engine
    engine = TrustScoringEngine(config)
    
    # Example URLs to score
    test_urls = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://httpbin.org",
        "https://www.google.com"
    ]
    
    print(f"Scoring {len(test_urls)} websites...")
    print()
    
    # Score each URL
    results = []
    for url in test_urls:
        print(f"Scoring: {url}")
        try:
            result = await engine.score_website(url)
            results.append(result)
            
            # Display results
            print(f"  Final Score: {result.final_score:.3f}")
            print(f"  Trust Level: {result.trust_level.name}")
            print(f"  Confidence: {result.confidence:.3f}")
            print(f"  Security: {result.security_score:.3f}")
            print(f"  Reputation: {result.reputation_score:.3f}")
            print(f"  Compliance: {result.compliance_score:.3f}")
            
            if result.warnings:
                print(f"  Warnings: {', '.join(result.warnings)}")
            
            if result.errors:
                print(f"  Errors: {', '.join(result.errors)}")
            
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
            print()
    
    # Generate summary report
    print("Summary Report")
    print("=" * 50)
    
    if results:
        avg_score = sum(r.final_score for r in results) / len(results)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        print(f"Average Score: {avg_score:.3f}")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print()
        
        # Categorize by trust level
        trust_levels = {}
        for result in results:
            level = result.trust_level.name
            if level not in trust_levels:
                trust_levels[level] = []
            trust_levels[level].append(result.url)
        
        for level, urls in trust_levels.items():
            print(f"{level}: {len(urls)} websites")
            for url in urls:
                print(f"  - {url}")
            print()
    
    # Save detailed results to file
    output_file = "scoring_results.json"
    with open(output_file, 'w') as f:
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_results.append({
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
        
        json.dump(serializable_results, f, indent=2)
    
    print(f"Detailed results saved to: {output_file}")
    
    # Demonstrate individual scorer usage
    print("\nIndividual Scorer Examples")
    print("=" * 50)
    
    from aihint.scoring.scorers import SSLTLSValidator, SecurityHeadersAnalyzer
    
    # SSL/TLS example
    print("SSL/TLS Validation Example:")
    ssl_validator = SSLTLSValidator()
    ssl_score, ssl_metrics = await ssl_validator.score("https://example.com")
    print(f"  Score: {ssl_score:.3f}")
    print(f"  Details: {json.dumps(ssl_metrics, indent=2)}")
    print()
    
    # Security Headers example
    print("Security Headers Analysis Example:")
    headers_analyzer = SecurityHeadersAnalyzer()
    headers_score, headers_metrics = await headers_analyzer.score("https://example.com")
    print(f"  Score: {headers_score:.3f}")
    print(f"  Headers Analyzed: {headers_metrics.get('headers_analyzed', 0)}")
    print(f"  Headers Present: {headers_metrics.get('headers_present', 0)}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
