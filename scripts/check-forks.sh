#!/bin/bash
# Check if repositories have been forked

echo "🔍 Checking if repositories have been forked..."
echo ""

# Check claude-code-action
echo "1. Checking claude-code-action..."
if curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/RyotaKuzuya/claude-code-action | grep -q "200"; then
    echo "✅ claude-code-action has been forked!"
else
    echo "❌ claude-code-action NOT forked yet"
    echo "   Please fork: https://github.com/anthropics/claude-code-action"
fi

echo ""

# Check claude-code-base-action
echo "2. Checking claude-code-base-action..."
if curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/RyotaKuzuya/claude-code-base-action | grep -q "200"; then
    echo "✅ claude-code-base-action has been forked!"
else
    echo "❌ claude-code-base-action NOT forked yet"
    echo "   Please fork: https://github.com/anthropics/claude-code-base-action"
fi

echo ""
echo "Once both repositories are forked, run:"
echo "./setup-claude-oauth-secrets.sh"