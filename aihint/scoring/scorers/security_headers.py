"""
Security Headers Analyzer

Analyzes HTTP security headers for security scoring.
"""

import aiohttp
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse


class SecurityHeadersAnalyzer:
    """Analyzes HTTP security headers for trust scoring."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 10)
        
        # Define security headers and their scoring criteria
        self.security_headers = {
            'Strict-Transport-Security': {
                'weight': 0.25,
                'required': True,
                'check_function': self._check_hsts
            },
            'Content-Security-Policy': {
                'weight': 0.2,
                'required': True,
                'check_function': self._check_csp
            },
            'X-Frame-Options': {
                'weight': 0.15,
                'required': True,
                'check_function': self._check_x_frame_options
            },
            'X-Content-Type-Options': {
                'weight': 0.1,
                'required': True,
                'check_function': self._check_x_content_type_options
            },
            'Referrer-Policy': {
                'weight': 0.1,
                'required': False,
                'check_function': self._check_referrer_policy
            },
            'Permissions-Policy': {
                'weight': 0.1,
                'required': False,
                'check_function': self._check_permissions_policy
            },
            'X-XSS-Protection': {
                'weight': 0.05,
                'required': False,
                'check_function': self._check_x_xss_protection
            },
            'Cache-Control': {
                'weight': 0.05,
                'required': False,
                'check_function': self._check_cache_control
            }
        }
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score security headers for the given URL.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Fetch headers
            headers = await self._fetch_headers(url)
            
            # Analyze each security header
            header_results = []
            total_score = 0.0
            max_score = 0.0
            
            for header_name, header_config in self.security_headers.items():
                check_function = header_config['check_function']
                weight = header_config['weight']
                required = header_config['required']
                
                header_value = headers.get(header_name, '')
                result = await check_function(header_name, header_value, required)
                
                header_results.append(result)
                total_score += result['score'] * weight
                max_score += weight
            
            final_score = total_score / max_score if max_score > 0 else 0.0
            
            return final_score, {
                'security_headers_score': final_score,
                'headers_analyzed': len(header_results),
                'headers_present': len([r for r in header_results if r['present']]),
                'headers_missing': len([r for r in header_results if not r['present'] and r['required']]),
                'header_details': header_results,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Security headers analysis failed for {url}: {e}")
            return 0.0, {
                'security_headers_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _fetch_headers(self, url: str) -> Dict[str, str]:
        """Fetch HTTP headers from the URL."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, allow_redirects=True) as response:
                    return dict(response.headers)
        except Exception as e:
            self.logger.warning(f"Failed to fetch headers from {url}: {e}")
            return {}
    
    async def _check_hsts(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check HSTS header configuration."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'HSTS header missing',
                'recommendation': 'Add Strict-Transport-Security header'
            }
        
        # Parse HSTS directive
        directives = {}
        for directive in value.split(';'):
            directive = directive.strip()
            if '=' in directive:
                key, val = directive.split('=', 1)
                directives[key.strip()] = val.strip()
            else:
                directives[directive] = True
        
        score = 0.0
        issues = []
        
        # Check max-age
        if 'max-age' in directives:
            try:
                max_age = int(directives['max-age'])
                if max_age >= 31536000:  # 1 year
                    score += 0.5
                elif max_age >= 86400:  # 1 day
                    score += 0.4
                elif max_age >= 3600:  # 1 hour
                    score += 0.3
                else:
                    issues.append('max-age too short')
            except ValueError:
                issues.append('invalid max-age value')
        else:
            issues.append('max-age missing')
        
        # Check includeSubDomains
        if 'includeSubDomains' in directives:
            score += 0.3
        else:
            issues.append('includeSubDomains not set')
        
        # Check preload
        if 'preload' in directives:
            score += 0.2
        else:
            issues.append('preload not set')
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': min(score, 1.0),
            'message': f"HSTS configured: {value}",
            'issues': issues,
            'directives': directives
        }
    
    async def _check_csp(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check Content Security Policy header."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'CSP header missing',
                'recommendation': 'Add Content-Security-Policy header'
            }
        
        # Basic CSP analysis
        score = 0.0
        directives = {}
        issues = []
        
        # Parse directives
        for directive in value.split(';'):
            directive = directive.strip()
            if ' ' in directive:
                key, *values = directive.split()
                directives[key] = values
            else:
                directives[directive] = []
        
        # Check for important directives
        important_directives = ['default-src', 'script-src', 'style-src', 'img-src']
        for directive in important_directives:
            if directive in directives:
                score += 0.2
            else:
                issues.append(f'{directive} missing')
        
        # Check for unsafe-inline/unsafe-eval
        for directive, values in directives.items():
            if 'unsafe-inline' in values:
                issues.append(f'{directive} allows unsafe-inline')
                score -= 0.1
            if 'unsafe-eval' in values:
                issues.append(f'{directive} allows unsafe-eval')
                score -= 0.1
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': max(0.0, min(score, 1.0)),
            'message': f"CSP configured: {len(directives)} directives",
            'issues': issues,
            'directives': list(directives.keys())
        }
    
    async def _check_x_frame_options(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check X-Frame-Options header."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'X-Frame-Options header missing',
                'recommendation': 'Add X-Frame-Options header'
            }
        
        value_lower = value.lower()
        if value_lower == 'deny':
            score = 1.0
            message = 'X-Frame-Options set to DENY (most secure)'
        elif value_lower.startswith('sameorigin'):
            score = 0.8
            message = 'X-Frame-Options set to SAMEORIGIN'
        elif value_lower.startswith('allow-from'):
            score = 0.5
            message = 'X-Frame-Options set to ALLOW-FROM (deprecated)'
        else:
            score = 0.3
            message = f'X-Frame-Options set to unknown value: {value}'
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': score,
            'message': message
        }
    
    async def _check_x_content_type_options(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check X-Content-Type-Options header."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'X-Content-Type-Options header missing',
                'recommendation': 'Add X-Content-Type-Options: nosniff'
            }
        
        if value.lower() == 'nosniff':
            score = 1.0
            message = 'X-Content-Type-Options set to nosniff'
        else:
            score = 0.0
            message = f'X-Content-Type-Options set to invalid value: {value}'
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': score,
            'message': message
        }
    
    async def _check_referrer_policy(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check Referrer-Policy header."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'Referrer-Policy header missing',
                'recommendation': 'Add Referrer-Policy header'
            }
        
        value_lower = value.lower()
        if value_lower in ['no-referrer', 'same-origin']:
            score = 1.0
            message = f'Referrer-Policy set to {value} (most secure)'
        elif value_lower in ['strict-origin', 'strict-origin-when-cross-origin']:
            score = 0.8
            message = f'Referrer-Policy set to {value} (good)'
        elif value_lower in ['origin', 'origin-when-cross-origin']:
            score = 0.6
            message = f'Referrer-Policy set to {value} (moderate)'
        else:
            score = 0.3
            message = f'Referrer-Policy set to unknown value: {value}'
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': score,
            'message': message
        }
    
    async def _check_permissions_policy(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check Permissions-Policy header."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'Permissions-Policy header missing',
                'recommendation': 'Add Permissions-Policy header'
            }
        
        # Basic analysis - more features = better security
        features = len(value.split(','))
        score = min(features * 0.1, 1.0)
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': score,
            'message': f'Permissions-Policy configured with {features} features'
        }
    
    async def _check_x_xss_protection(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check X-XSS-Protection header."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'X-XSS-Protection header missing',
                'recommendation': 'Add X-XSS-Protection header (deprecated but still useful)'
            }
        
        if '1' in value and 'mode=block' in value:
            score = 1.0
            message = 'X-XSS-Protection properly configured'
        elif '1' in value:
            score = 0.5
            message = 'X-XSS-Protection enabled but not in block mode'
        else:
            score = 0.0
            message = f'X-XSS-Protection set to invalid value: {value}'
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': score,
            'message': message
        }
    
    async def _check_cache_control(self, header_name: str, value: str, required: bool) -> Dict[str, Any]:
        """Check Cache-Control header for security."""
        if not value:
            return {
                'header': header_name,
                'present': False,
                'required': required,
                'score': 0.0,
                'message': 'Cache-Control header missing',
                'recommendation': 'Add Cache-Control header'
            }
        
        value_lower = value.lower()
        score = 0.0
        
        if 'no-store' in value_lower:
            score += 0.5
        if 'no-cache' in value_lower:
            score += 0.3
        if 'private' in value_lower:
            score += 0.2
        
        return {
            'header': header_name,
            'present': True,
            'required': required,
            'score': min(score, 1.0),
            'message': f'Cache-Control configured: {value}'
        }
