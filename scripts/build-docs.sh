#!/bin/bash

# Build AIHint documentation locally

set -e

echo "Building AIHint documentation..."

# Install documentation dependencies
pip install -r docs-requirements.txt

# Build the documentation
mkdocs build

echo "Documentation built successfully!"
echo "You can view it by opening docs/site/index.html in your browser"
echo "Or serve it with: mkdocs serve" 