#!/bin/bash

echo "🧪 GitHub Actions Claude テスト確認"
echo "===================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}✅ GitHub Secretsの更新が完了しました！${NC}"
echo ""

echo -e "${BLUE}テスト方法：${NC}"
echo ""

echo "1. 新しいIssueを作成:"
echo "   https://github.com/RyotaKuzuya/webai-search-service/issues/new"
echo ""

echo "2. Issue内容の例:"
echo "   タイトル: Claude OAuth Token Test"
echo "   本文: Testing new OAuth token setup"
echo ""

echo "3. Issue作成後、コメントを追加:"
echo -e "${YELLOW}   @claude${NC}"
echo "   こんにちは！新しいOAuthトークンでテストです。"
echo ""

echo "4. 数秒待つと、Claudeが自動的に応答します"
echo ""

echo -e "${GREEN}期待される結果：${NC}"
echo "- GitHub ActionsのClaude Code Actionが起動"
echo "- Claudeがコメントに返信"
echo "- ワークフローが「success」で完了"
echo ""

echo "もしエラーが発生した場合:"
echo "- Actions タブでワークフローログを確認"
echo "- https://github.com/RyotaKuzuya/webai-search-service/actions"