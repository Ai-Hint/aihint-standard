"""
Domain Reputation Checker

Checks domain reputation using various sources and databases.
"""

import aiohttp
import asyncio
import logging
import whois
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse


class DomainReputationChecker:
    """Checks domain reputation using multiple sources."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 10)
        
        # Reputation sources configuration
        self.sources = {
            'whois': {
                'enabled': True,
                'weight': 0.4
            },
            'blacklists': {
                'enabled': True,
                'weight': 0.3,
                'lists': [
                    'https://www.spamhaus.org/dbl/',
                    'https://www.surbl.org/',
                    'https://www.phishtank.com/'
                ]
            },
            'dns_reputation': {
                'enabled': True,
                'weight': 0.3
            }
        }
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score domain reputation for the given URL.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            # Run reputation checks in parallel
            check_tasks = []
            
            if self.sources['whois']['enabled']:
                check_tasks.append(self._check_whois_reputation(domain))
            
            if self.sources['blacklists']['enabled']:
                check_tasks.append(self._check_blacklists(domain))
            
            if self.sources['dns_reputation']['enabled']:
                check_tasks.append(self._check_dns_reputation(domain))
            
            # Execute all checks
            results = await asyncio.gather(*check_tasks, return_exceptions=True)
            
            # Process results
            check_results = []
            total_score = 0.0
            max_score = 0.0
            issues = []
            
            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(f"Reputation check failed: {result}")
                    continue
                
                check_results.append(result)
                weight = result.get('weight', 1.0)
                total_score += result['score'] * weight
                max_score += weight
                
                if result.get('issues'):
                    issues.extend(result['issues'])
            
            # Calculate final score
            final_score = total_score / max_score if max_score > 0 else 0.5
            
            return final_score, {
                'domain_reputation_score': final_score,
                'domain': domain,
                'issues_found': len(issues),
                'issues': issues,
                'check_details': check_results,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Domain reputation checking failed for {url}: {e}")
            return 0.0, {
                'domain_reputation_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_whois_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation using WHOIS data."""
        try:
            # Get WHOIS information
            whois_data = whois.whois(domain)
            
            score = 1.0
            issues = []
            details = {}
            
            # Check registration date
            if hasattr(whois_data, 'creation_date') and whois_data.creation_date:
                creation_date = whois_data.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                age_days = (datetime.now() - creation_date).days
                details['age_days'] = age_days
                
                if age_days < 30:
                    issues.append('Very new domain (< 30 days)')
                    score -= 0.3
                elif age_days < 365:
                    issues.append('New domain (< 1 year)')
                    score -= 0.1
            
            # Check expiration date
            if hasattr(whois_data, 'expiration_date') and whois_data.expiration_date:
                exp_date = whois_data.expiration_date
                if isinstance(exp_date, list):
                    exp_date = exp_date[0]
                
                days_until_expiry = (exp_date - datetime.now()).days
                details['days_until_expiry'] = days_until_expiry
                
                if days_until_expiry < 30:
                    issues.append('Domain expires soon (< 30 days)')
                    score -= 0.2
            
            # Check registrar
            if hasattr(whois_data, 'registrar') and whois_data.registrar:
                registrar = whois_data.registrar.lower()
                details['registrar'] = registrar
                
                # Check for suspicious registrars
                suspicious_registrars = ['namecheap', 'godaddy', 'enom']
                if any(susp in registrar for susp in suspicious_registrars):
                    # These are actually legitimate, but we can check for patterns
                    pass
            
            # Check nameservers
            if hasattr(whois_data, 'name_servers') and whois_data.name_servers:
                nameservers = whois_data.name_servers
                if isinstance(nameservers, list):
                    details['nameservers'] = nameservers
                    
                    # Check for suspicious nameserver patterns
                    for ns in nameservers:
                        if 'ns1.' in ns.lower() or 'ns2.' in ns.lower():
                            # Generic nameservers might indicate less professional setup
                            pass
            
            return {
                'check': 'whois_reputation',
                'score': max(0.0, score),
                'weight': self.sources['whois']['weight'],
                'issues': issues,
                'details': details,
                'message': f'WHOIS analysis: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'whois_reputation',
                'score': 0.5,
                'weight': self.sources['whois']['weight'],
                'error': str(e),
                'message': 'WHOIS check failed'
            }
    
    async def _check_blacklists(self, domain: str) -> Dict[str, Any]:
        """Check domain against various blacklists."""
        try:
            # For now, implement basic blacklist checking
            # In production, this would integrate with actual blacklist APIs
            
            score = 1.0
            issues = []
            blacklist_results = []
            
            # Simulate blacklist checks (replace with real API calls)
            blacklists = [
                {'name': 'Spamhaus DBL', 'url': f'https://www.spamhaus.org/dbl/lookup/{domain}'},
                {'name': 'SURBL', 'url': f'https://www.surbl.org/surbl-analysis/{domain}'},
                {'name': 'PhishTank', 'url': f'https://www.phishtank.com/phish_detail.php?phish_id={domain}'}
            ]
            
            for blacklist in blacklists:
                # Simulate check (replace with actual HTTP request)
                is_listed = False  # This would be determined by actual API response
                
                blacklist_results.append({
                    'name': blacklist['name'],
                    'listed': is_listed,
                    'url': blacklist['url']
                })
                
                if is_listed:
                    issues.append(f'Listed on {blacklist["name"]}')
                    score -= 0.3
            
            return {
                'check': 'blacklists',
                'score': max(0.0, score),
                'weight': self.sources['blacklists']['weight'],
                'issues': issues,
                'blacklist_results': blacklist_results,
                'message': f'Blacklist check: {len(issues)} listings found'
            }
            
        except Exception as e:
            return {
                'check': 'blacklists',
                'score': 0.5,
                'weight': self.sources['blacklists']['weight'],
                'error': str(e),
                'message': 'Blacklist check failed'
            }
    
    async def _check_dns_reputation(self, domain: str) -> Dict[str, Any]:
        """Check DNS reputation and configuration."""
        try:
            import socket
            import dns.resolver
            
            score = 1.0
            issues = []
            dns_details = {}
            
            # Check A record
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                dns_details['a_records'] = [str(record) for record in a_records]
                
                # Check for suspicious IP patterns
                for record in a_records:
                    ip = str(record)
                    # Check for private IPs (might indicate hosting issues)
                    if ip.startswith(('10.', '192.168.', '172.')):
                        issues.append('Domain resolves to private IP')
                        score -= 0.2
                    
                    # Check for known suspicious IP ranges
                    if ip.startswith('127.'):
                        issues.append('Domain resolves to localhost')
                        score -= 0.5
                        
            except Exception as e:
                issues.append('No A record found')
                score -= 0.3
            
            # Check MX record
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                dns_details['mx_records'] = [str(record) for record in mx_records]
            except:
                issues.append('No MX record found')
                score -= 0.1
            
            # Check NS records
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                dns_details['ns_records'] = [str(record) for record in ns_records]
                
                # Check for suspicious nameservers
                for record in ns_records:
                    ns = str(record).lower()
                    if 'ns1.' in ns or 'ns2.' in ns:
                        # Generic nameservers might indicate less professional setup
                        pass
                        
            except Exception as e:
                issues.append('No NS records found')
                score -= 0.2
            
            # Check TXT records for SPF, DKIM, DMARC
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                txt_data = [str(record) for record in txt_records]
                dns_details['txt_records'] = txt_data
                
                # Check for SPF record
                has_spf = any('v=spf1' in record for record in txt_data)
                if not has_spf:
                    issues.append('No SPF record found')
                    score -= 0.1
                
                # Check for DMARC record
                has_dmarc = any('v=DMARC1' in record for record in txt_data)
                if not has_dmarc:
                    issues.append('No DMARC record found')
                    score -= 0.1
                    
            except:
                issues.append('No TXT records found')
                score -= 0.1
            
            return {
                'check': 'dns_reputation',
                'score': max(0.0, score),
                'weight': self.sources['dns_reputation']['weight'],
                'issues': issues,
                'dns_details': dns_details,
                'message': f'DNS analysis: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'dns_reputation',
                'score': 0.5,
                'weight': self.sources['dns_reputation']['weight'],
                'error': str(e),
                'message': 'DNS reputation check failed'
            }
