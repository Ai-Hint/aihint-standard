# Contributing to AIHint

Thank you for your interest in contributing to AIHint! This document provides guidelines and information for contributors.

## Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs
- Use the GitHub issue tracker
- Include detailed steps to reproduce
- Provide environment information (OS, Python version, etc.)

### Suggesting Enhancements
- Open a feature request issue
- Describe the use case and benefits
- Consider implementation complexity

### Code Contributions
- Fork the repository
- Create a feature branch (`git checkout -b feature/amazing-feature`)
- Make your changes
- Add tests for new functionality
- Ensure all tests pass
- Update documentation if needed
- Submit a pull request

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/aihint-standard.git
   cd aihint-standard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for all public functions
- Keep functions focused and concise

## Testing

- Write tests for new functionality
- Ensure existing tests continue to pass
- Aim for good test coverage
- Use descriptive test names

## Documentation

- Update relevant documentation when adding features
- Include examples for new functionality
- Keep API documentation current

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md with a note describing your changes
3. The PR will be merged once you have the sign-off of at least one maintainer

## Release Process

1. Update version in `setup.py` and `aihint/__init__.py`
2. Update CHANGELOG.md
3. Create a release tag
4. Publish to PyPI (if applicable)

## Questions?

If you have questions about contributing, please open an issue or reach out to the maintainers.

Thank you for contributing to AIHint! 