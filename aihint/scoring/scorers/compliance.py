"""
Compliance Checker

Checks for legal compliance indicators and regulatory adherence.
"""

import aiohttp
import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse, urljoin


class ComplianceChecker:
    """Checks for legal compliance and regulatory adherence."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 10)
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score legal compliance and regulatory adherence.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            # Run enhanced compliance checks
            compliance_checks = await asyncio.gather(
                self._check_terms_of_service(url),
                self._check_cookie_compliance(url),
                self._check_accessibility_compliance(url),
                self._check_legal_notices(url),
                self._check_business_registration(url),
                self._check_regulatory_compliance(url),
                self._check_data_protection_compliance(url),
                return_exceptions=True
            )
            
            # Process results
            total_score = 0.0
            max_score = 0.0
            all_issues = []
            check_results = []
            
            for result in compliance_checks:
                if isinstance(result, Exception):
                    self.logger.warning(f"Compliance check failed: {result}")
                    continue
                
                check_results.append(result)
                total_score += result['score']
                max_score += 1.0
                
                if result.get('issues'):
                    all_issues.extend(result['issues'])
            
            final_score = total_score / max_score if max_score > 0 else 0.5
            
            return final_score, {
                'compliance_score': final_score,
                'issues_found': len(all_issues),
                'issues': all_issues,
                'check_details': check_results,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Compliance checking failed for {url}: {e}")
            return 0.0, {
                'compliance_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_business_registration(self, url: str) -> Dict[str, Any]:
        """Check for business registration and legal entity verification."""
        try:
            # Simulate business registration checking
            registration_score = 0.5  # Default moderate score
            issues = []
            details = {}
            
            # Check for business indicators
            business_indicators = [
                'about', 'company', 'business', 'corporate', 'inc', 'llc', 'ltd',
                'corporation', 'incorporated', 'limited'
            ]
            
            # Check URL and content for business indicators
            if any(indicator in url.lower() for indicator in business_indicators):
                registration_score = 0.8
                details['business_indicators'] = 'Found business-related terms in URL'
            
            # Check for contact information (would be more detailed in real implementation)
            if 'contact' in url.lower() or 'about' in url.lower():
                registration_score = min(1.0, registration_score + 0.2)
                details['contact_pages'] = 'Contact/about pages found'
            
            return {
                'check': 'business_registration',
                'score': registration_score,
                'issues': issues,
                'details': details,
                'message': f'Business registration check: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'business_registration',
                'score': 0.3,
                'issues': ['Business registration check failed'],
                'error': str(e),
                'message': 'Business registration check failed'
            }
    
    async def _check_regulatory_compliance(self, url: str) -> Dict[str, Any]:
        """Check for regulatory compliance indicators."""
        try:
            # Simulate regulatory compliance checking
            compliance_score = 0.7  # Default moderate score
            issues = []
            details = {}
            
            # Check for regulatory compliance indicators
            compliance_indicators = [
                'privacy', 'terms', 'legal', 'compliance', 'gdpr', 'ccpa',
                'regulatory', 'policy', 'disclaimer'
            ]
            
            # Check URL for compliance indicators
            found_indicators = [indicator for indicator in compliance_indicators 
                              if indicator in url.lower()]
            
            if found_indicators:
                compliance_score = min(1.0, compliance_score + 0.2)
                details['compliance_indicators'] = found_indicators
            
            return {
                'check': 'regulatory_compliance',
                'score': compliance_score,
                'issues': issues,
                'details': details,
                'message': f'Regulatory compliance check: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'regulatory_compliance',
                'score': 0.3,
                'issues': ['Regulatory compliance check failed'],
                'error': str(e),
                'message': 'Regulatory compliance check failed'
            }
    
    async def _check_data_protection_compliance(self, url: str) -> Dict[str, Any]:
        """Check for data protection and privacy compliance."""
        try:
            # Simulate data protection compliance checking
            protection_score = 0.6  # Default moderate score
            issues = []
            details = {}
            
            # Check for data protection indicators
            protection_indicators = [
                'privacy', 'data-protection', 'gdpr', 'ccpa', 'cookie-policy',
                'data-policy', 'privacy-policy'
            ]
            
            # Check URL for protection indicators
            found_indicators = [indicator for indicator in protection_indicators 
                              if indicator in url.lower()]
            
            if found_indicators:
                protection_score = min(1.0, protection_score + 0.3)
                details['protection_indicators'] = found_indicators
            
            return {
                'check': 'data_protection_compliance',
                'score': protection_score,
                'issues': issues,
                'details': details,
                'message': f'Data protection compliance check: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'data_protection_compliance',
                'score': 0.3,
                'issues': ['Data protection compliance check failed'],
                'error': str(e),
                'message': 'Data protection compliance check failed'
            }
    
    async def _check_terms_of_service(self, url: str) -> Dict[str, Any]:
        """Check for terms of service availability and quality."""
        try:
            # Find terms of service
            terms_url = await self._find_terms_of_service(url)
            
            if not terms_url:
                return {
                    'check': 'terms_of_service',
                    'score': 0.3,
                    'issues': ['No terms of service found'],
                    'message': 'Terms of service not found'
                }
            
            # Analyze terms content
            terms_analysis = await self._analyze_terms_content(terms_url)
            
            return {
                'check': 'terms_of_service',
                'score': terms_analysis['score'],
                'issues': terms_analysis['issues'],
                'details': terms_analysis['details'],
                'message': f'Terms of service analysis: {len(terms_analysis["issues"])} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'terms_of_service',
                'score': 0.5,
                'issues': [],
                'error': str(e),
                'message': 'Terms of service check failed'
            }
    
    async def _check_cookie_compliance(self, url: str) -> Dict[str, Any]:
        """Check for cookie compliance and GDPR adherence."""
        try:
            # Check for cookie banner/notice
            cookie_banner = await self._check_cookie_banner(url)
            
            # Check for cookie policy
            cookie_policy = await self._find_cookie_policy(url)
            
            score = 0.0
            issues = []
            details = {}
            
            if cookie_banner:
                score += 0.5
                details['cookie_banner'] = True
            else:
                score += 0.2  # Give some credit even without banner
                issues.append('No cookie banner/notice found')
            
            if cookie_policy:
                score += 0.3
                details['cookie_policy'] = cookie_policy
            else:
                issues.append('No cookie policy found')
            
            # Check for cookie consent mechanisms
            consent_mechanisms = await self._check_consent_mechanisms(url)
            if consent_mechanisms:
                score += 0.2
                details['consent_mechanisms'] = consent_mechanisms
            
            return {
                'check': 'cookie_compliance',
                'score': min(score, 1.0),
                'issues': issues,
                'details': details,
                'message': f'Cookie compliance: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'cookie_compliance',
                'score': 0.5,
                'issues': [],
                'error': str(e),
                'message': 'Cookie compliance check failed'
            }
    
    async def _check_accessibility_compliance(self, url: str) -> Dict[str, Any]:
        """Check for accessibility compliance indicators."""
        try:
            # Basic accessibility checks
            accessibility_checks = await self._run_accessibility_checks(url)
            
            score = 0.0
            issues = []
            details = {}
            
            # Check for alt text on images
            if accessibility_checks.get('alt_text_ratio', 0) > 0.8:
                score += 0.3
            else:
                issues.append('Missing alt text on images')
            
            # Check for heading structure
            if accessibility_checks.get('has_heading_structure', False):
                score += 0.2
            else:
                issues.append('Poor heading structure')
            
            # Check for form labels
            if accessibility_checks.get('form_labels_ratio', 0) > 0.8:
                score += 0.2
            else:
                issues.append('Missing form labels')
            
            # Check for ARIA attributes
            if accessibility_checks.get('has_aria_attributes', False):
                score += 0.2
            else:
                issues.append('No ARIA attributes found')
            
            # Check for skip links
            if accessibility_checks.get('has_skip_links', False):
                score += 0.1
            else:
                issues.append('No skip links found')
            
            details.update(accessibility_checks)
            
            return {
                'check': 'accessibility_compliance',
                'score': min(score, 1.0),
                'issues': issues,
                'details': details,
                'message': f'Accessibility compliance: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'accessibility_compliance',
                'score': 0.5,
                'issues': [],
                'error': str(e),
                'message': 'Accessibility compliance check failed'
            }
    
    async def _check_legal_notices(self, url: str) -> Dict[str, Any]:
        """Check for legal notices and disclaimers."""
        try:
            # Find legal notices
            legal_pages = await self._find_legal_pages(url)
            
            score = 0.0
            issues = []
            details = {'legal_pages': legal_pages}
            
            if legal_pages:
                score += 0.5
                
                # Analyze legal content
                legal_analysis = await self._analyze_legal_content(legal_pages)
                score += legal_analysis['score'] * 0.5
                issues.extend(legal_analysis['issues'])
                details.update(legal_analysis['details'])
            else:
                issues.append('No legal notices found')
            
            return {
                'check': 'legal_notices',
                'score': min(score, 1.0),
                'issues': issues,
                'details': details,
                'message': f'Legal notices: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'check': 'legal_notices',
                'score': 0.5,
                'issues': [],
                'error': str(e),
                'message': 'Legal notices check failed'
            }
    
    async def _find_terms_of_service(self, url: str) -> str:
        """Find terms of service URL."""
        try:
            terms_patterns = [
                '/terms',
                '/terms-of-service',
                '/terms_of_service',
                '/terms.html',
                '/terms.php',
                '/legal/terms',
                '/agreement',
                '/user-agreement'
            ]
            
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            for pattern in terms_patterns:
                terms_url = urljoin(base_url, pattern)
                if await self._check_url_exists(terms_url):
                    return terms_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"Terms of service search failed: {e}")
            return None
    
    async def _analyze_terms_content(self, terms_url: str) -> Dict[str, Any]:
        """Analyze terms of service content."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(terms_url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        return {'score': 0.0, 'issues': ['Terms not accessible'], 'details': {}}
                    
                    content = await response.text()
                    content_lower = content.lower()
                    
                    score = 0.0
                    issues = []
                    details = {}
                    
                    # Check for important legal sections
                    required_sections = [
                        'liability',
                        'disclaimer',
                        'governing law',
                        'jurisdiction',
                        'user responsibilities',
                        'prohibited uses',
                        'termination',
                        'modifications'
                    ]
                    
                    sections_found = [section for section in required_sections if section in content_lower]
                    details['sections_found'] = sections_found
                    details['sections_missing'] = [s for s in required_sections if s not in sections_found]
                    
                    score += len(sections_found) * 0.1
                    
                    if len(sections_found) < 4:
                        issues.append('Missing important legal sections')
                    
                    # Check content length
                    word_count = len(content.split())
                    details['word_count'] = word_count
                    
                    if word_count > 1000:
                        score += 0.2
                    elif word_count < 500:
                        issues.append('Terms too short')
                        score -= 0.1
                    
                    return {
                        'score': min(score, 1.0),
                        'issues': issues,
                        'details': details
                    }
                    
        except Exception as e:
            return {'score': 0.0, 'issues': [f'Analysis failed: {e}'], 'details': {}}
    
    async def _check_cookie_banner(self, url: str) -> bool:
        """Check for cookie banner presence."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        return False
                    
                    content = await response.text()
                    content_lower = content.lower()
                    
                    # Look for cookie banner indicators
                    cookie_indicators = [
                        'cookie consent',
                        'cookie banner',
                        'accept cookies',
                        'cookie notice',
                        'gdpr consent',
                        'cookie policy'
                    ]
                    
                    return any(indicator in content_lower for indicator in cookie_indicators)
                    
        except Exception as e:
            self.logger.warning(f"Cookie banner check failed: {e}")
            return False
    
    async def _find_cookie_policy(self, url: str) -> str:
        """Find cookie policy URL."""
        try:
            cookie_patterns = [
                '/cookie-policy',
                '/cookie_policy',
                '/cookies',
                '/cookie.html',
                '/privacy#cookies'
            ]
            
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            for pattern in cookie_patterns:
                cookie_url = urljoin(base_url, pattern)
                if await self._check_url_exists(cookie_url):
                    return cookie_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cookie policy search failed: {e}")
            return None
    
    async def _check_consent_mechanisms(self, url: str) -> List[str]:
        """Check for consent mechanisms."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        return []
                    
                    content = await response.text()
                    content_lower = content.lower()
                    
                    mechanisms = []
                    
                    if 'accept' in content_lower and 'cookie' in content_lower:
                        mechanisms.append('accept_button')
                    
                    if 'decline' in content_lower and 'cookie' in content_lower:
                        mechanisms.append('decline_button')
                    
                    if 'settings' in content_lower and 'cookie' in content_lower:
                        mechanisms.append('settings_button')
                    
                    return mechanisms
                    
        except Exception as e:
            self.logger.warning(f"Consent mechanisms check failed: {e}")
            return []
    
    async def _run_accessibility_checks(self, url: str) -> Dict[str, Any]:
        """Run basic accessibility checks."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        return {}
                    
                    content = await response.text()
                    
                    # Count images with and without alt text
                    img_tags = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
                    img_with_alt = len(re.findall(r'<img[^>]*alt\s*=', content, re.IGNORECASE))
                    alt_text_ratio = img_with_alt / len(img_tags) if img_tags else 1.0
                    
                    # Check for heading structure
                    headings = re.findall(r'<h[1-6][^>]*>', content, re.IGNORECASE)
                    has_heading_structure = len(headings) > 0
                    
                    # Check for form labels
                    form_tags = re.findall(r'<form[^>]*>', content, re.IGNORECASE)
                    label_tags = re.findall(r'<label[^>]*>', content, re.IGNORECASE)
                    form_labels_ratio = len(label_tags) / len(form_tags) if form_tags else 1.0
                    
                    # Check for ARIA attributes
                    has_aria_attributes = bool(re.search(r'aria-', content, re.IGNORECASE))
                    
                    # Check for skip links
                    has_skip_links = bool(re.search(r'skip.*content|skip.*navigation', content, re.IGNORECASE))
                    
                    return {
                        'alt_text_ratio': alt_text_ratio,
                        'has_heading_structure': has_heading_structure,
                        'form_labels_ratio': form_labels_ratio,
                        'has_aria_attributes': has_aria_attributes,
                        'has_skip_links': has_skip_links
                    }
                    
        except Exception as e:
            self.logger.warning(f"Accessibility checks failed: {e}")
            return {}
    
    async def _find_legal_pages(self, url: str) -> List[str]:
        """Find legal pages on the website."""
        try:
            legal_patterns = [
                '/legal',
                '/legal-notice',
                '/disclaimer',
                '/terms',
                '/privacy',
                '/about/legal',
                '/company/legal'
            ]
            
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            legal_pages = []
            
            for pattern in legal_patterns:
                legal_url = urljoin(base_url, pattern)
                if await self._check_url_exists(legal_url):
                    legal_pages.append(legal_url)
            
            return legal_pages
            
        except Exception as e:
            self.logger.error(f"Legal pages search failed: {e}")
            return []
    
    async def _analyze_legal_content(self, legal_pages: List[str]) -> Dict[str, Any]:
        """Analyze legal content quality."""
        try:
            total_score = 0.0
            all_issues = []
            details = {'pages_analyzed': len(legal_pages)}
            
            for page_url in legal_pages:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(page_url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                            if response.status == 200:
                                content = await response.text()
                                content_lower = content.lower()
                                
                                # Check for legal language
                                legal_terms = ['liability', 'disclaimer', 'jurisdiction', 'governing law']
                                terms_found = [term for term in legal_terms if term in content_lower]
                                
                                if terms_found:
                                    total_score += 0.2
                                else:
                                    all_issues.append(f'Missing legal language on {page_url}')
                                
                except Exception as e:
                    all_issues.append(f'Failed to analyze {page_url}: {e}')
            
            return {
                'score': min(total_score, 1.0),
                'issues': all_issues,
                'details': details
            }
            
        except Exception as e:
            return {'score': 0.0, 'issues': [f'Legal content analysis failed: {e}'], 'details': {}}
    
    async def _check_url_exists(self, url: str) -> bool:
        """Check if URL exists and returns valid content."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
