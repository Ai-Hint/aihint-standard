#!/bin/bash

# AiHint Standard Release Script
# Usage: ./scripts/release.sh <version> [--dry-run]

set -e

VERSION=${1:-}
DRY_RUN=false

if [[ "$2" == "--dry-run" ]]; then
    DRY_RUN=true
fi

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version> [--dry-run]"
    echo "Example: $0 1.0.0"
    exit 1
fi

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 1.0.0)"
    exit 1
fi

echo "🚀 Preparing release v$VERSION"
if [[ "$DRY_RUN" == "true" ]]; then
    echo "📝 DRY RUN MODE - No changes will be made"
fi

# Function to update version in file
update_version() {
    local file=$1
    local pattern=$2
    local replacement=$3
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Would update $file: $pattern -> $replacement"
    else
        sed -i.bak "s/$pattern/$replacement/g" "$file"
        rm -f "$file.bak"
        echo "✅ Updated $file"
    fi
}

# Update Python version
echo "📦 Updating Python version..."
update_version "setup.py" "version='[^']*'" "version='$VERSION'"
update_version "aihint/__init__.py" "__version__ = '[^']*'" "__version__ = '$VERSION'"

# Update JavaScript version (main package.json)
echo "📦 Updating JavaScript version..."
update_version "package.json" '"version": "[^"]*"' '"version": "'$VERSION'"'

# Update PHP version
echo "📦 Updating PHP version..."
update_version "php-aihint/composer.json" '"version": "[^"]*"' '"version": "'$VERSION'"'

# Update documentation version
echo "📚 Updating documentation..."
update_version "mkdocs.yml" "site_name: AiHint Standard [^']*" "site_name: AiHint Standard v$VERSION"

# Run tests
echo "🧪 Running tests..."
if [[ "$DRY_RUN" == "false" ]]; then
    pytest
    echo "✅ Tests passed"
fi

# Build documentation
echo "📚 Building documentation..."
if [[ "$DRY_RUN" == "false" ]]; then
    mkdocs build
    echo "✅ Documentation built"
fi

# Check git status
echo "🔍 Checking git status..."
if [[ "$DRY_RUN" == "false" ]]; then
    git status
    echo ""
    echo "📋 Next steps:"
    echo "1. Review changes: git diff"
    echo "2. Add files: git add ."
    echo "3. Commit: git commit -m 'Release v$VERSION'"
    echo "4. Tag: git tag -a v$VERSION -m 'Release v$VERSION'"
    echo "5. Push: git push origin main && git push origin v$VERSION"
    echo ""
    echo "📦 Package publishing:"
    echo "- Python: python setup.py sdist bdist_wheel && twine upload dist/*"
    echo "- JavaScript: npm publish"
    echo "- PHP: Update Packagist (if using)"
else
    echo "📋 Would perform the following actions:"
    echo "- Update version numbers in all files"
    echo "- Run tests"
    echo "- Build documentation"
    echo "- Create git tag and push"
fi

echo ""
echo "🎉 Release preparation complete for v$VERSION" 