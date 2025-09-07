"""
Privacy Policy Analyzer

Analyzes privacy policy presence and content for compliance scoring.
"""

import aiohttp
import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse, urljoin


class PrivacyPolicyAnalyzer:
    """Analyzes privacy policy for compliance and trustworthiness."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 10)
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score privacy policy presence and quality.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            # Find privacy policy URL
            privacy_url = await self._find_privacy_policy(url)
            
            if not privacy_url:
                return 0.0, {
                    'privacy_policy_score': 0.0,
                    'privacy_url': None,
                    'message': 'No privacy policy found',
                    'success': True,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Analyze privacy policy content
            analysis = await self._analyze_privacy_policy(privacy_url)
            
            return analysis['score'], {
                'privacy_policy_score': analysis['score'],
                'privacy_url': privacy_url,
                'analysis': analysis,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Privacy policy analysis failed for {url}: {e}")
            return 0.0, {
                'privacy_policy_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _find_privacy_policy(self, url: str) -> str:
        """Find privacy policy URL on the website."""
        try:
            # Common privacy policy URL patterns
            privacy_patterns = [
                '/privacy',
                '/privacy-policy',
                '/privacy_policy',
                '/privacy.html',
                '/privacy.php',
                '/legal/privacy',
                '/terms/privacy',
                '/privacy-notice',
                '/data-protection',
                '/gdpr'
            ]
            
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            # Check common privacy policy locations
            for pattern in privacy_patterns:
                privacy_url = urljoin(base_url, pattern)
                if await self._check_url_exists(privacy_url):
                    return privacy_url
            
            # Try to find privacy policy link on main page
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Look for privacy policy links
                            privacy_links = re.findall(
                                r'href=["\']([^"\']*(?:privacy|data.protection|gdpr)[^"\']*)["\']',
                                content,
                                re.IGNORECASE
                            )
                            
                            for link in privacy_links:
                                full_url = urljoin(url, link)
                                if await self._check_url_exists(full_url):
                                    return full_url
                                    
            except Exception as e:
                self.logger.warning(f"Failed to search for privacy policy links: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Privacy policy search failed: {e}")
            return None
    
    async def _check_url_exists(self, url: str) -> bool:
        """Check if URL exists and returns valid content."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
    
    async def _analyze_privacy_policy(self, privacy_url: str) -> Dict[str, Any]:
        """Analyze privacy policy content for compliance indicators."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(privacy_url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        return {
                            'score': 0.0,
                            'message': 'Privacy policy not accessible',
                            'details': {}
                        }
                    
                    content = await response.text()
                    content_lower = content.lower()
                    
                    # Analyze content for compliance indicators
                    score = 0.0
                    details = {}
                    issues = []
                    
                    # Check for required sections
                    required_sections = [
                        'data collection',
                        'data usage',
                        'data sharing',
                        'cookies',
                        'contact information',
                        'data retention',
                        'user rights',
                        'data security'
                    ]
                    
                    sections_found = []
                    for section in required_sections:
                        if section in content_lower:
                            sections_found.append(section)
                            score += 0.1
                    
                    details['sections_found'] = sections_found
                    details['sections_missing'] = [s for s in required_sections if s not in sections_found]
                    
                    # Check for GDPR compliance indicators
                    gdpr_indicators = [
                        'gdpr',
                        'general data protection regulation',
                        'data protection officer',
                        'lawful basis',
                        'data subject rights',
                        'consent',
                        'legitimate interest'
                    ]
                    
                    gdpr_found = [indicator for indicator in gdpr_indicators if indicator in content_lower]
                    details['gdpr_indicators'] = gdpr_found
                    
                    if len(gdpr_found) >= 3:
                        score += 0.2
                    elif len(gdpr_found) >= 1:
                        score += 0.1
                    
                    # Check for CCPA compliance indicators
                    ccpa_indicators = [
                        'ccpa',
                        'california consumer privacy act',
                        'do not sell',
                        'opt-out',
                        'consumer rights'
                    ]
                    
                    ccpa_found = [indicator for indicator in ccpa_indicators if indicator in content_lower]
                    details['ccpa_indicators'] = ccpa_found
                    
                    if len(ccpa_found) >= 2:
                        score += 0.1
                    
                    # Check for contact information
                    contact_patterns = [
                        r'email[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                        r'phone[:\s]+([0-9\-\+\(\)\s]{10,})',
                        r'address[:\s]+([^<\n]{20,})'
                    ]
                    
                    contact_found = []
                    for pattern in contact_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            contact_found.extend(matches)
                    
                    details['contact_info'] = contact_found
                    if contact_found:
                        score += 0.1
                    
                    # Check for update date
                    date_patterns = [
                        r'last updated[:\s]+([a-zA-Z0-9\s,]+)',
                        r'effective date[:\s]+([a-zA-Z0-9\s,]+)',
                        r'updated[:\s]+([a-zA-Z0-9\s,]+)'
                    ]
                    
                    dates_found = []
                    for pattern in date_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            dates_found.extend(matches)
                    
                    details['dates_found'] = dates_found
                    if dates_found:
                        score += 0.1
                    
                    # Check content length (longer policies are generally better)
                    word_count = len(content.split())
                    details['word_count'] = word_count
                    
                    if word_count > 2000:
                        score += 0.1
                    elif word_count > 1000:
                        score += 0.05
                    elif word_count < 500:
                        issues.append('Privacy policy too short')
                        score -= 0.1
                    
                    # Check for legal language indicators
                    legal_terms = [
                        'terms of service',
                        'terms and conditions',
                        'legal notice',
                        'disclaimer',
                        'liability',
                        'jurisdiction'
                    ]
                    
                    legal_found = [term for term in legal_terms if term in content_lower]
                    details['legal_terms'] = legal_found
                    
                    if len(legal_found) >= 3:
                        score += 0.1
                    
                    # Final score adjustment
                    if score > 1.0:
                        score = 1.0
                    
                    return {
                        'score': score,
                        'message': f'Privacy policy analysis: {len(sections_found)}/{len(required_sections)} sections found',
                        'details': details,
                        'issues': issues
                    }
                    
        except Exception as e:
            return {
                'score': 0.0,
                'message': f'Privacy policy analysis failed: {e}',
                'details': {},
                'issues': ['Analysis failed']
            }
