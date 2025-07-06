"""
Setup script for AIHint Python package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aihint",
    version="0.1.0",
    author="AIHint Contributors",
    author_email="contributors@aihint.org",
    description="AIHint Standard Implementation - Create, validate, and verify AIHint metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aihint/aihint-standard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aihint=aihint.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "aihint": ["schema/*.json"],
    },
    keywords="aihint, metadata, trust, verification, cryptography",
    project_urls={
        "Bug Reports": "https://github.com/aihint/aihint-standard/issues",
        "Source": "https://github.com/aihint/aihint-standard",
        "Documentation": "https://github.com/aihint/aihint-standard#readme",
    },
) 