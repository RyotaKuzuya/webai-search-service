#!/bin/bash
# Setup script to run after forking repositories

echo "🚀 Claude OAuth Setup After Fork"
echo "================================"
echo ""

# Check if forks exist
./check-forks.sh

echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Add GitHub Secrets:"
echo "   Go to: https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
echo ""
echo "   Add these secrets:"
echo "   - CLAUDE_ACCESS_TOKEN"
echo "   - CLAUDE_REFRESH_TOKEN"
echo "   - CLAUDE_EXPIRES_AT"
echo ""
echo "2. Test the setup:"
echo "   - Go to: https://github.com/RyotaKuzuya/webai-search-service/actions"
echo "   - Run 'Test Claude OAuth Setup' workflow"
echo ""
echo "3. Or test with an issue comment:"
echo "   - Create a new issue"
echo "   - Comment: @claude Hello, are you working?"
echo ""

# Show the OAuth tokens for easy copy
echo "📋 Your OAuth Tokens (from Claude config):"
echo "=========================================="
echo ""
echo "CLAUDE_ACCESS_TOKEN:"
cat /home/ubuntu/webai/claude-config/claude_config.json | jq -r '.access_token'
echo ""
echo "CLAUDE_REFRESH_TOKEN:"
cat /home/ubuntu/webai/claude-config/claude_config.json | jq -r '.refresh_token'
echo ""
echo "CLAUDE_EXPIRES_AT:"
cat /home/ubuntu/webai/claude-config/claude_config.json | jq -r '.expires_at'
echo ""
echo "=========================================="