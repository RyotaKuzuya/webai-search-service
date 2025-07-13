#!/bin/bash

echo "🚀 Claude OAuth クイックセットアップ"
echo "===================================="
echo ""

# Claude CLIの確認
if ! command -v claude &> /dev/null; then
    echo "❌ Claude CLIがインストールされていません"
    echo ""
    echo "インストール:"
    echo "curl -fsSL https://cli.claude.ai/install.sh | sh"
    exit 1
fi

echo "✅ Claude CLI: $(claude --version)"
echo ""

echo "📝 手動でトークンを生成してください:"
echo ""
echo "1. ターミナルで実行:"
echo "   claude setup-token"
echo ""
echo "2. 生成されたトークンを確認:"
echo "   cat ~/.config/claude/claude_config.json | jq -r '.oauth_token'"
echo ""
echo "3. GitHub Secretsに登録:"
echo "   https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
echo "   Name: CLAUDE_CODE_OAUTH_TOKEN"
echo "   Value: 生成されたトークン"
echo ""
echo "4. テスト:"
echo "   新しいIssueで @claude メンション"
echo ""
echo "以上の手順を実行してください。"