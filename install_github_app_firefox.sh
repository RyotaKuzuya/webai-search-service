#!/bin/bash

echo "🦊 Firefox で GitHub App をインストール"
echo "========================================"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}ステップ1: Claude GitHub App のインストール${NC}"
echo ""

# Firefoxがインストールされているか確認
if command -v firefox &> /dev/null; then
    echo "FirefoxでGitHub Appページを開きます..."
    firefox "https://github.com/apps/claude" &
    echo -e "${GREEN}✅ Firefoxでページを開きました${NC}"
else
    echo -e "${YELLOW}Firefoxが見つかりません。手動でURLを開いてください：${NC}"
    echo "https://github.com/apps/claude"
fi

echo ""
echo -e "${BLUE}手順：${NC}"
echo "1. ページが開いたら 'Install' ボタンをクリック"
echo "2. リポジトリを選択:"
echo "   - 'RyotaKuzuya/webai-search-service' を選択"
echo "3. 'Install' をクリックして完了"
echo ""

echo -e "${YELLOW}すでにインストール済みの場合：${NC}"
echo "- 'Configure' ボタンが表示されます"
echo "- その場合、設定を確認してください"
echo ""

echo -e "${BLUE}ステップ2: 認証トークンの確認${NC}"
echo ""
echo "現在設定されているトークン："
echo "- CLAUDE_ACCESS_TOKEN ✅"
echo "- CLAUDE_REFRESH_TOKEN ✅"
echo "- CLAUDE_EXPIRES_AT ✅"
echo ""

echo -e "${BLUE}ステップ3: ワークフローの確認${NC}"
echo ""
echo "ワークフローファイル: .github/workflows/claude-max-plan.yml"
echo "- claude-code-action@main を使用"
echo "- OAuth認証設定済み"
echo ""

echo -e "${GREEN}準備完了後：${NC}"
echo "1. 新しいIssueでテスト"
echo "2. @claude メンション"
echo "3. Actionsタブで結果確認"
echo ""

echo "手動でブラウザを開く場合のURL："
echo -e "${YELLOW}https://github.com/apps/claude${NC}"