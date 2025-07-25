#!/bin/bash
# Initialize Claude Code session with Context-Driven Spec Development

echo "🚀 Initializing Claude Code with Context-Driven Spec Development..."
echo ""

if [[ -f ~/.claude/METHODOLOGY.md ]]; then
    echo "📚 Global methodology detected"
    echo "Start your session with:"
    echo "  'Please read ~/.claude/METHODOLOGY.md and .claude/PROJECT_CONTEXT.md'"
else
    echo "📚 Standalone project setup detected"
    echo "Start your session with:"
    echo "  'Please read .claude/METHODOLOGY.md and .claude/PROJECT_CONTEXT.md'"
fi

echo ""
echo "Then begin feature development with:"
echo "  'Let's explore requirements for [feature]'"
echo ""
echo "Available commands:"
echo "  /analyze [scope]     - Analyze codebase patterns"
echo "  /refine [aspect]     - Refine specifications"
echo "  /review [type]       - Review quality and completeness"
echo ""
