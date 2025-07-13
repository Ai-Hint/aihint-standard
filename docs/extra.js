// SEO and Analytics Enhancements

// Add structured data for better SEO
document.addEventListener('DOMContentLoaded', function() {
    // Add JSON-LD structured data
    const structuredData = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "AiHint Standard",
        "description": "An open standard for signed, verifiable metadata for websites",
        "url": "https://docs.aihint.org/",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Cross-platform",
        "programmingLanguage": ["Python", "JavaScript", "PHP"],
        "license": "https://opensource.org/licenses/MIT",
        "author": {
            "@type": "Organization",
            "name": "AiHint Contributors",
            "url": "https://github.com/Ai-Hint/aihint-standard"
        },
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "keywords": [
            "aihint", "website metadata", "digital signatures", "trust verification",
            "security", "open standard", "cryptography", "website trust",
            "metadata signing", "verification protocol"
        ]
    };

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(structuredData);
    document.head.appendChild(script);

    // Add meta description if not present
    if (!document.querySelector('meta[name="description"]')) {
        const meta = document.createElement('meta');
        meta.name = 'description';
        meta.content = 'AiHint Standard provides signed, verifiable metadata for websites. Multi-language support (Python, JavaScript, PHP) with CLI tools and comprehensive documentation.';
        document.head.appendChild(meta);
    }

    // Add canonical URL
    if (!document.querySelector('link[rel="canonical"]')) {
        const canonical = document.createElement('link');
        canonical.rel = 'canonical';
        canonical.href = window.location.href;
        document.head.appendChild(canonical);
    }
});

// Enhanced search functionality
if (typeof mkdocs !== 'undefined' && mkdocs.search) {
    // Improve search indexing
    mkdocs.search.index = mkdocs.search.index || {};
    
    // Add custom search terms
    const customTerms = [
        'aihint', 'metadata', 'signatures', 'verification', 'trust',
        'python', 'javascript', 'php', 'cli', 'api', 'security',
        'cryptography', 'digital signatures', 'website trust'
    ];
    
    customTerms.forEach(term => {
        if (mkdocs.search.index[term] === undefined) {
            mkdocs.search.index[term] = [];
        }
    });
}

// Analytics tracking (if Google Analytics is configured)
if (typeof gtag !== 'undefined') {
    // Track page views
    gtag('config', 'GA_MEASUREMENT_ID', {
        'page_title': document.title,
        'page_location': window.location.href
    });
}

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }
    });
}
