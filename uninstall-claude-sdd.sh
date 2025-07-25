#!/bin/bash
# Uninstall Project Context-Driven Spec Development

echo "Removing project Context-Driven SDD installation..."
read -p "This will remove .claude/ directory and init script. Continue? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "/Users/br/proj/claude-code-dev-logger/.claude/"
    rm -f "/Users/br/proj/claude-code-dev-logger/init-claude.sh"
    rm -f "/Users/br/proj/claude-code-dev-logger/uninstall-claude-sdd.sh"
    echo "✅ Project uninstallation complete."
else
    echo "❌ Uninstallation cancelled."
fi
