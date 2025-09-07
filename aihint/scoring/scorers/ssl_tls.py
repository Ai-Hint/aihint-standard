"""
SSL/TLS Validation Scorer

Validates SSL/TLS configuration and certificate chain for security scoring.
"""

import ssl
import socket
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from urllib.parse import urlparse

from ..metrics import MetricResult, MetricStatus


class SSLTLSValidator:
    """Validates SSL/TLS configuration and certificates."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 10)
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score SSL/TLS configuration for the given URL.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            
            # Run SSL checks
            ssl_checks = await asyncio.gather(
                self._check_certificate_validity(hostname, port),
                self._check_cipher_strength(hostname, port),
                self._check_protocol_version(hostname, port),
                self._check_certificate_chain(hostname, port),
                return_exceptions=True
            )
            
            # Process results
            results = []
            total_score = 0.0
            max_score = 0.0
            
            for i, check_result in enumerate(ssl_checks):
                if isinstance(check_result, Exception):
                    results.append({
                        'check': f'check_{i}',
                        'success': False,
                        'error': str(check_result),
                        'score': 0.0
                    })
                else:
                    results.append(check_result)
                    total_score += check_result['score']
                    max_score += 1.0
            
            final_score = total_score / max_score if max_score > 0 else 0.0
            
            return final_score, {
                'ssl_tls_score': final_score,
                'checks': results,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"SSL/TLS validation failed for {url}: {e}")
            return 0.0, {
                'ssl_tls_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_certificate_validity(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check if SSL certificate is valid and not expired."""
        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    import datetime
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.datetime.now()).days
                    
                    if days_until_expiry > 90:
                        score = 1.0
                        message = f"Certificate valid for {days_until_expiry} days"
                    elif days_until_expiry > 30:
                        score = 0.9
                        message = f"Certificate valid for {days_until_expiry} days"
                    elif days_until_expiry > 0:
                        score = 0.7
                        message = f"Certificate expires in {days_until_expiry} days"
                    else:
                        score = 0.0
                        message = "Certificate has expired"
                    
                    return {
                        'check': 'certificate_validity',
                        'success': True,
                        'score': score,
                        'message': message,
                        'details': {
                            'issuer': cert.get('issuer', {}),
                            'subject': cert.get('subject', {}),
                            'not_after': cert['notAfter'],
                            'days_until_expiry': days_until_expiry
                        }
                    }
                    
        except Exception as e:
            return {
                'check': 'certificate_validity',
                'success': False,
                'score': 0.0,
                'error': str(e)
            }
    
    async def _check_cipher_strength(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check cipher strength and encryption quality."""
        try:
            context = ssl.create_default_context()
            context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
            
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()
                    
                    if cipher:
                        protocol, cipher_name, bits = cipher
                        
                        # Score based on key length and cipher strength
                        if bits >= 256:
                            score = 1.0
                            message = f"Strong encryption: {cipher_name} ({bits} bits)"
                        elif bits >= 128:
                            score = 0.9
                            message = f"Good encryption: {cipher_name} ({bits} bits)"
                        elif bits >= 112:
                            score = 0.7
                            message = f"Acceptable encryption: {cipher_name} ({bits} bits)"
                        else:
                            score = 0.3
                            message = f"Weak encryption: {cipher_name} ({bits} bits)"
                        
                        return {
                            'check': 'cipher_strength',
                            'success': True,
                            'score': score,
                            'message': message,
                            'details': {
                                'protocol': protocol,
                                'cipher': cipher_name,
                                'key_length': bits
                            }
                        }
                    else:
                        return {
                            'check': 'cipher_strength',
                            'success': False,
                            'score': 0.0,
                            'error': 'No cipher information available'
                        }
                        
        except Exception as e:
            return {
                'check': 'cipher_strength',
                'success': False,
                'score': 0.0,
                'error': str(e)
            }
    
    async def _check_protocol_version(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check TLS protocol version."""
        try:
            # Test different TLS versions
            tls_versions = {
                'TLSv1.3': ssl.PROTOCOL_TLS,
                'TLSv1.2': ssl.PROTOCOL_TLSv1_2,
                'TLSv1.1': ssl.PROTOCOL_TLSv1_1,
                'TLSv1.0': ssl.PROTOCOL_TLSv1
            }
            
            supported_versions = []
            
            for version_name, protocol in tls_versions.items():
                try:
                    context = ssl.SSLContext(protocol)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            supported_versions.append(version_name)
                except:
                    continue
            
            # Score based on supported versions
            if 'TLSv1.3' in supported_versions:
                score = 1.0
                message = "Supports latest TLS 1.3"
            elif 'TLSv1.2' in supported_versions and 'TLSv1.1' not in supported_versions:
                score = 0.95
                message = "Supports TLS 1.2 only (excellent)"
            elif 'TLSv1.2' in supported_versions:
                score = 0.85
                message = "Supports TLS 1.2 and older versions (good)"
            elif 'TLSv1.1' in supported_versions:
                score = 0.6
                message = "Supports TLS 1.1 and older versions"
            else:
                score = 0.2
                message = "Only supports older TLS versions"
            
            return {
                'check': 'protocol_version',
                'success': True,
                'score': score,
                'message': message,
                'details': {
                    'supported_versions': supported_versions
                }
            }
            
        except Exception as e:
            return {
                'check': 'protocol_version',
                'success': False,
                'score': 0.0,
                'error': str(e)
            }
    
    async def _check_certificate_chain(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check certificate chain completeness."""
        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate issuer and subject
                    issuer = cert.get('issuer', {})
                    subject = cert.get('subject', {})
                    
                    # Basic chain validation - check if issuer and subject are different
                    # (indicating a proper chain vs self-signed)
                    if issuer and subject and issuer != subject:
                        score = 1.0
                        message = "Valid certificate chain (issuer != subject)"
                    else:
                        score = 0.7
                        message = "Single certificate (may be self-signed)"
                    
                    return {
                        'check': 'certificate_chain',
                        'success': True,
                        'score': score,
                        'message': message,
                        'details': {
                            'issuer': issuer,
                            'subject': subject,
                            'has_chain': issuer != subject if issuer and subject else False
                        }
                    }
                    
        except Exception as e:
            return {
                'check': 'certificate_chain',
                'success': False,
                'score': 0.0,
                'error': str(e)
            }
