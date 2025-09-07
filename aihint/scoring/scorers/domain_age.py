"""
Domain Age Analyzer

Analyzes domain age and historical data for reputation scoring.
"""

import asyncio
import logging
import whois
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
from urllib.parse import urlparse


class DomainAgeAnalyzer:
    """Analyzes domain age and historical characteristics."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score domain age and historical data.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            # Get WHOIS data
            whois_data = whois.whois(domain)
            
            score = 1.0
            issues = []
            details = {}
            
            # Analyze domain age
            if hasattr(whois_data, 'creation_date') and whois_data.creation_date:
                creation_date = whois_data.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                age_days = (datetime.now() - creation_date).days
                details['age_days'] = age_days
                details['creation_date'] = creation_date.isoformat()
                
                # Score based on age
                if age_days < 1:
                    score = 0.1
                    issues.append('Domain created today')
                elif age_days < 7:
                    score = 0.2
                    issues.append('Domain created this week')
                elif age_days < 30:
                    score = 0.4
                    issues.append('Domain created this month')
                elif age_days < 90:
                    score = 0.6
                    issues.append('Domain created this quarter')
                elif age_days < 365:
                    score = 0.8
                    issues.append('Domain created this year')
                else:
                    score = 1.0
                    details['age_category'] = 'established'
            
            # Check for recent changes
            if hasattr(whois_data, 'updated_date') and whois_data.updated_date:
                updated_date = whois_data.updated_date
                if isinstance(updated_date, list):
                    updated_date = updated_date[0]
                
                days_since_update = (datetime.now() - updated_date).days
                details['days_since_update'] = days_since_update
                details['updated_date'] = updated_date.isoformat()
                
                if days_since_update < 7:
                    issues.append('Domain recently updated')
                    score -= 0.1
            
            # Check expiration
            if hasattr(whois_data, 'expiration_date') and whois_data.expiration_date:
                exp_date = whois_data.expiration_date
                if isinstance(exp_date, list):
                    exp_date = exp_date[0]
                
                days_until_expiry = (exp_date - datetime.now()).days
                details['days_until_expiry'] = days_until_expiry
                details['expiration_date'] = exp_date.isoformat()
                
                if days_until_expiry < 30:
                    issues.append('Domain expires soon')
                    score -= 0.2
                elif days_until_expiry < 90:
                    issues.append('Domain expires in 3 months')
                    score -= 0.1
            
            # Check registrar reputation
            if hasattr(whois_data, 'registrar') and whois_data.registrar:
                registrar = whois_data.registrar
                details['registrar'] = registrar
                
                # Basic registrar reputation check
                reputable_registrars = [
                    'GoDaddy', 'Namecheap', 'Google Domains', 'Cloudflare',
                    'Network Solutions', 'Register.com', '1&1 IONOS'
                ]
                
                if not any(rep in registrar for rep in reputable_registrars):
                    issues.append('Unknown or less reputable registrar')
                    score -= 0.1
            
            return max(0.0, score), {
                'domain_age_score': max(0.0, score),
                'domain': domain,
                'age_analysis': details,
                'issues_found': len(issues),
                'issues': issues,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Domain age analysis failed for {url}: {e}")
            return 0.0, {
                'domain_age_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
