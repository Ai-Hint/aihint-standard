# Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation Options

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/aihint/aihint-standard.git
cd aihint-standard

# Install in development mode
pip install -e .
```

### Option 2: Install Dependencies Only

```bash
# Install required dependencies
pip install -r requirements.txt
```

### Option 3: Install from PyPI (Future)

```bash
# When available on PyPI
pip install aihint
```

## Dependencies

The following packages are required:

- `cryptography>=41.0.0` - Cryptographic operations
- `requests>=2.31.0` - HTTP requests for key fetching
- `jsonschema>=4.19.0` - JSON schema validation
- `click>=8.1.0` - CLI framework
- `pydantic>=2.4.0` - Data validation
- `pytest>=7.0.0` - Testing framework

## Verification

After installation, verify that AiHint is working:

```bash
# Check CLI is available
aihint --help

# Run tests
python -m pytest tests/ -v

# Run example
python examples/create_hint.py
```

## Development Setup

For contributors:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r docs-requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Build documentation
mkdocs build
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're in the correct directory and have installed the package
2. **Permission Error**: Use `pip install --user` or create a virtual environment
3. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv aihint-env

# Activate (Linux/Mac)
source aihint-env/bin/activate

# Activate (Windows)
aihint-env\Scripts\activate

# Install
pip install -e .
``` 