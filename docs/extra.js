// Make the repository link open in a new tab
// This is the current approach since MkDocs Material doesn't support this via config
window.addEventListener('DOMContentLoaded', function() {
  // Try multiple selectors for compatibility with different MkDocs Material versions
  var repoLink = document.querySelector('a.md-header__source, a.md-source, a[href*="github.com"]');
  if (repoLink) {
    repoLink.setAttribute('target', '_blank');
    repoLink.setAttribute('rel', 'noopener noreferrer');
  }
  
  // Update copyright year dynamically
  var yearSpan = document.getElementById('current-year');
  if (yearSpan) {
    var currentYear = new Date().getFullYear();
    yearSpan.textContent = currentYear;
  }
}); 