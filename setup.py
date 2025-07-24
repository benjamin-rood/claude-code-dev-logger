#!/usr/bin/env python3
"""
Setup script for Claude Code Dev Logger
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version from package
version_file = this_directory / "claude_logger" / "__init__.py"
version = {}
with open(version_file) as f:
    exec(f.read(), version)

setup(
    name="claude-code-dev-logger",
    version=version['__version__'],
    author=version['__author__'],
    author_email=version['__email__'],
    description="Conversation logging and analysis tool for Claude Code CLI development workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benjamin-rood/claude-code-dev-logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "claude-logger=claude_logger.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="claude ai development logging analysis methodology tracking",
    project_urls={
        "Bug Reports": "https://github.com/benjamin-rood/claude-code-dev-logger/issues",
        "Source": "https://github.com/benjamin-rood/claude-code-dev-logger",
        "Documentation": "https://github.com/benjamin-rood/claude-code-dev-logger/blob/main/README.md",
    },
)