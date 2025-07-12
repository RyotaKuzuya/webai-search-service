#!/bin/bash

echo "🔑 Claude Max Plan OAuth Token生成（公式方法）"
echo "=============================================="
echo ""
echo "Claude CLIの setup-token コマンドを使用してOAuthトークンを生成します。"
echo ""
echo "このコマンドは対話的な操作が必要なため、以下の手順を手動で実行してください："
echo ""
echo "1. 新しいターミナルウィンドウを開く"
echo "2. 以下のコマンドを実行："
echo ""
echo "   claude setup-token"
echo ""
echo "3. 生成されたトークンをコピー"
echo "4. GitHubリポジトリの Settings > Secrets > Actions で以下を設定："
echo "   - Name: CLAUDE_CODE_OAUTH_TOKEN"
echo "   - Value: 生成されたトークン"
echo ""
echo "5. ワークフローを以下のように更新："
echo ""
cat << 'EOF'
- uses: anthropics/claude-code-action@beta
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
EOF
echo ""
echo "注意: これはClaude Max個人利用向けです。チーム開発にはAPIキーを使用してください。"