#!/bin/bash
"""
Installation script for Claude Code Dev Logger
"""

set -e

echo "Installing Claude Code Dev Logger..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"

# Install the package
echo "Installing claude-logger package..."
pip3 install -e .

echo "✓ Package installed successfully"

# Verify installation
echo "Verifying installation..."
if command -v claude-logger &> /dev/null; then
    echo "✓ claude-logger command is available"
    echo ""
    echo "Installation complete! You can now use:"
    echo "  claude-logger --help                    # Show help"
    echo "  claude-logger --track-energy [args]     # Run with energy tracking"
    echo "  claude-logger --analyze                 # Analyze existing sessions"
    echo "  claude-logger --list-sessions           # List all sessions"
    echo ""
    echo "The logger will create session logs in ~/.claude-logs/"
else
    echo "Warning: claude-logger command not found in PATH"
    echo "You may need to add the pip install location to your PATH"
    echo "or run: python3 -m claude_logger.cli instead"
fi