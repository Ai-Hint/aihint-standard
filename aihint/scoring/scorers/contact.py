"""
Contact Information Validator

Validates contact information availability and quality for trust scoring.
"""

import aiohttp
import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse, urljoin


class ContactValidator:
    """Validates contact information for trustworthiness."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 10)
    
    async def score(self, url: str) -> Tuple[float, Dict[str, Any]]:
        """
        Score contact information availability and quality.
        
        Returns:
            Tuple of (score, detailed_metrics)
        """
        try:
            # Find contact information on the website
            contact_info = await self._find_contact_information(url)
            
            # Enhanced contact analysis
            analysis = self._analyze_contact_quality(contact_info)
            
            # Additional business validation
            business_validation = await self._validate_business_contact(contact_info, url)
            
            # Combine scores
            combined_score = (analysis['score'] + business_validation['score']) / 2
            
            return combined_score, {
                'contact_score': combined_score,
                'contact_info': contact_info,
                'analysis': analysis,
                'business_validation': business_validation,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Contact validation failed for {url}: {e}")
            return 0.0, {
                'contact_score': 0.0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _validate_business_contact(self, contact_info: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Validate business contact information and registration."""
        try:
            score = 0.5  # Default moderate score
            validation_details = {}
            issues = []
            
            # Check for business email domains
            professional_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            business_domains = []
            
            for email in contact_info.get('emails', []):
                domain = email.split('@')[-1].lower() if '@' in email else ''
                if domain and domain not in professional_domains:
                    business_domains.append(domain)
            
            if business_domains:
                score += 0.2
                validation_details['business_domains'] = business_domains
            
            # Check for physical addresses
            if contact_info.get('addresses'):
                score += 0.2
                validation_details['physical_addresses'] = len(contact_info['addresses'])
            
            # Check for phone numbers
            if contact_info.get('phone_numbers'):
                score += 0.1
                validation_details['phone_numbers'] = len(contact_info['phone_numbers'])
            
            # Check for social media presence
            if contact_info.get('social_media'):
                score += 0.1
                validation_details['social_media'] = len(contact_info['social_media'])
            
            # Check for business registration indicators
            business_indicators = ['inc', 'llc', 'ltd', 'corp', 'company', 'business']
            if any(indicator in url.lower() for indicator in business_indicators):
                score += 0.1
                validation_details['business_indicators'] = 'Found in URL'
            
            return {
                'score': min(1.0, score),
                'details': validation_details,
                'issues': issues,
                'message': f'Business validation: {len(issues)} issues found'
            }
            
        except Exception as e:
            return {
                'score': 0.3,
                'details': {},
                'issues': ['Business validation failed'],
                'error': str(e),
                'message': 'Business validation failed'
            }
    
    async def _find_contact_information(self, url: str) -> Dict[str, Any]:
        """Find contact information on the website."""
        try:
            contact_info = {
                'emails': [],
                'phones': [],
                'addresses': [],
                'contact_pages': [],
                'social_media': []
            }
            
            # Check common contact page locations
            contact_pages = await self._find_contact_pages(url)
            contact_info['contact_pages'] = contact_pages
            
            # Extract contact info from main page and contact pages
            pages_to_check = [url] + contact_pages
            
            for page_url in pages_to_check:
                try:
                    page_info = await self._extract_contact_from_page(page_url)
                    
                    contact_info['emails'].extend(page_info['emails'])
                    contact_info['phones'].extend(page_info['phones'])
                    contact_info['addresses'].extend(page_info['addresses'])
                    contact_info['social_media'].extend(page_info['social_media'])
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract contact info from {page_url}: {e}")
            
            # Remove duplicates
            for key in contact_info:
                if isinstance(contact_info[key], list):
                    contact_info[key] = list(set(contact_info[key]))
            
            return contact_info
            
        except Exception as e:
            self.logger.error(f"Contact information search failed: {e}")
            return {'emails': [], 'phones': [], 'addresses': [], 'contact_pages': [], 'social_media': []}
    
    async def _find_contact_pages(self, url: str) -> List[str]:
        """Find contact page URLs."""
        try:
            contact_patterns = [
                '/contact',
                '/contact-us',
                '/contact_us',
                '/contact.html',
                '/contact.php',
                '/about/contact',
                '/support/contact',
                '/help/contact',
                '/get-in-touch',
                '/reach-us'
            ]
            
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            contact_pages = []
            
            # Check common contact page patterns
            for pattern in contact_patterns:
                contact_url = urljoin(base_url, pattern)
                if await self._check_url_exists(contact_url):
                    contact_pages.append(contact_url)
            
            # Search for contact links on main page
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Look for contact links
                            contact_links = re.findall(
                                r'href=["\']([^"\']*(?:contact|about|support|help)[^"\']*)["\']',
                                content,
                                re.IGNORECASE
                            )
                            
                            for link in contact_links:
                                full_url = urljoin(url, link)
                                if await self._check_url_exists(full_url):
                                    contact_pages.append(full_url)
                                    
            except Exception as e:
                self.logger.warning(f"Failed to search for contact links: {e}")
            
            return list(set(contact_pages))
            
        except Exception as e:
            self.logger.error(f"Contact page search failed: {e}")
            return []
    
    async def _check_url_exists(self, url: str) -> bool:
        """Check if URL exists and returns valid content."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
    
    async def _extract_contact_from_page(self, url: str) -> Dict[str, List[str]]:
        """Extract contact information from a specific page."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        return {'emails': [], 'phones': [], 'addresses': [], 'social_media': []}
                    
                    content = await response.text()
                    
                    # Extract emails
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    emails = re.findall(email_pattern, content)
                    
                    # Extract phone numbers
                    phone_patterns = [
                        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
                        r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}',
                        r'\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
                    ]
                    
                    phones = []
                    for pattern in phone_patterns:
                        phones.extend(re.findall(pattern, content))
                    
                    # Extract addresses (basic pattern)
                    address_pattern = r'[0-9]+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir|Court|Ct)'
                    addresses = re.findall(address_pattern, content, re.IGNORECASE)
                    
                    # Extract social media links
                    social_patterns = [
                        r'https?://(?:www\.)?(?:facebook|twitter|linkedin|instagram|youtube|tiktok)\.com/[a-zA-Z0-9._-]+',
                        r'@[a-zA-Z0-9_]+'  # Social media handles
                    ]
                    
                    social_media = []
                    for pattern in social_patterns:
                        social_media.extend(re.findall(pattern, content, re.IGNORECASE))
                    
                    return {
                        'emails': emails,
                        'phones': phones,
                        'addresses': addresses,
                        'social_media': social_media
                    }
                    
        except Exception as e:
            self.logger.warning(f"Failed to extract contact info from {url}: {e}")
            return {'emails': [], 'phones': [], 'addresses': [], 'social_media': []}
    
    def _analyze_contact_quality(self, contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of contact information."""
        score = 0.0
        details = {}
        issues = []
        
        # Score based on email availability
        emails = contact_info.get('emails', [])
        if emails:
            # Filter out common non-contact emails
            contact_emails = [email for email in emails if not any(
                domain in email.lower() for domain in ['noreply', 'no-reply', 'donotreply', 'admin', 'webmaster']
            )]
            
            if contact_emails:
                score += 0.3
                details['contact_emails'] = contact_emails
            else:
                issues.append('Only automated email addresses found')
                score += 0.1
        else:
            issues.append('No email addresses found')
        
        # Score based on phone availability
        phones = contact_info.get('phones', [])
        if phones:
            score += 0.2
            details['phones'] = phones
        else:
            issues.append('No phone numbers found')
        
        # Score based on address availability
        addresses = contact_info.get('addresses', [])
        if addresses:
            score += 0.2
            details['addresses'] = addresses
        else:
            issues.append('No physical addresses found')
        
        # Score based on contact pages
        contact_pages = contact_info.get('contact_pages', [])
        if contact_pages:
            score += 0.1
            details['contact_pages'] = contact_pages
        else:
            issues.append('No dedicated contact pages found')
        
        # Score based on social media presence
        social_media = contact_info.get('social_media', [])
        if social_media:
            score += 0.1
            details['social_media'] = social_media
        
        # Bonus for comprehensive contact information
        if len([item for item in [emails, phones, addresses] if item]) >= 2:
            score += 0.1
        
        # Check for professional email domains
        if emails:
            professional_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            professional_emails = [email for email in emails if any(
                domain in email.lower() for domain in professional_domains
            )]
            
            if len(professional_emails) == len(emails):
                issues.append('Only personal email addresses found')
                score -= 0.1
            else:
                details['professional_emails'] = [email for email in emails if email not in professional_emails]
        
        return {
            'score': max(0.0, min(score, 1.0)),
            'details': details,
            'issues': issues,
            'message': f'Contact analysis: {len(issues)} issues found'
        }
