// Make the repository link open in a new tab
window.addEventListener("DOMContentLoaded", function() {
  // Find all anchor tags in the header that link to the GitHub repo (case-insensitive)
  var githubLinks = Array.from(document.querySelectorAll("a")).filter(function(link) {
    return /github\.com\/(aihint|Ai-Hint)\/aihint-standard/i.test(link.href);
  });
  githubLinks.forEach(function(link) {
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");
  });

  // Update copyright year dynamically
  var yearSpan = document.getElementById("current-year");
  if (yearSpan) {
    var currentYear = new Date().getFullYear();
    yearSpan.textContent = currentYear;
  }
});
