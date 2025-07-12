#!/usr/bin/env python3
"""
Generate sitemap.xml from MkDocs configuration
"""

import yaml
import xml.etree.ElementTree as ET
from datetime import datetime
import os

def load_mkdocs_config():
    """Load MkDocs configuration"""
    with open('mkdocs.yml', 'r') as f:
        return yaml.safe_load(f)

def extract_urls_from_nav(nav, base_url="https://standard.aihint.org", base_path=""):
    """Recursively extract URLs from navigation structure"""
    urls = []
    
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if key == 'Home' and isinstance(value, str):
                    # Homepage
                    urls.append({
                        'loc': base_url + '/',
                        'priority': '1.0',
                        'changefreq': 'weekly'
                    })
                elif isinstance(value, list):
                    # Section with subsections
                    urls.extend(extract_urls_from_nav(value, base_url, base_path))
                elif isinstance(value, str):
                    # Direct page
                    page_path = value.replace('.md', '/')
                    if page_path == 'index/':
                        page_path = ''
                    urls.append({
                        'loc': base_url + '/' + page_path,
                        'priority': '0.8',
                        'changefreq': 'monthly'
                    })
    
    return urls

def create_sitemap(urls):
    """Create XML sitemap"""
    # Create root element
    root = ET.Element('urlset')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 
             'http://www.sitemaps.org/schemas/sitemap/0.9 '
             'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
    
    # Add URLs
    for url_info in urls:
        url_elem = ET.SubElement(root, 'url')
        
        loc = ET.SubElement(url_elem, 'loc')
        loc.text = url_info['loc']
        
        lastmod = ET.SubElement(url_elem, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
        
        changefreq = ET.SubElement(url_elem, 'changefreq')
        changefreq.text = url_info['changefreq']
        
        priority = ET.SubElement(url_elem, 'priority')
        priority.text = url_info['priority']
    
    return root

def write_sitemap(root, filename):
    """Write sitemap to file"""
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    
    with open(filename, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

def main():
    """Main function"""
    print("Generating sitemap...")
    
    # Load configuration
    config = load_mkdocs_config()
    
    # Extract URLs from navigation
    urls = extract_urls_from_nav(config['nav'])
    
    # Create sitemap
    root = create_sitemap(urls)
    
    # Write sitemap
    write_sitemap(root, 'docs/sitemap.xml')
    
    # Create compressed version
    import gzip
    with open('docs/sitemap.xml', 'rb') as f_in:
        with gzip.open('docs/sitemap.xml.gz', 'wb') as f_out:
            f_out.writelines(f_in)
    
    print(f"Generated sitemap with {len(urls)} URLs")
    print("Files created:")
    print("  - docs/sitemap.xml")
    print("  - docs/sitemap.xml.gz")

if __name__ == '__main__':
    main() 