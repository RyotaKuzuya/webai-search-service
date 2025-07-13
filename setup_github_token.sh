#!/bin/bash

echo "🔐 GitHub トークン設定ガイド"
echo "============================"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}ステップ1: 新しいGitHubトークンを作成${NC}"
echo ""
echo "1. 以下のURLにアクセス："
echo "   https://github.com/settings/tokens/new"
echo ""
echo "2. 以下の設定でトークンを作成："
echo "   - Note: webai-search-service-push"
echo "   - Expiration: 90 days (推奨)"
echo "   - Scopes: ☑ repo (Full control of private repositories)"
echo ""
echo "3. 'Generate token' をクリック"
echo "4. トークンをコピー (ghp_で始まる文字列)"
echo ""

echo -e "${YELLOW}トークンを入力してください (貼り付け後、Enter):${NC}"
read -s GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}エラー: トークンが入力されていません${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ トークンを受け取りました${NC}"
echo ""

echo -e "${BLUE}ステップ2: リモートURLを更新${NC}"
git remote set-url origin https://${GITHUB_TOKEN}@github.com/RyotaKuzuya/webai-search-service.git

echo -e "${GREEN}✓ リモートURLを更新しました${NC}"
echo ""

echo -e "${BLUE}ステップ3: GitHubにプッシュ${NC}"
git push origin master

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ プッシュ成功！${NC}"
    echo ""
    
    echo -e "${BLUE}ステップ4: 動作確認${NC}"
    echo ""
    echo "1. GitHub Actions を確認:"
    echo "   https://github.com/RyotaKuzuya/webai-search-service/actions"
    echo ""
    echo "2. 新しいIssueでテスト:"
    echo "   https://github.com/RyotaKuzuya/webai-search-service/issues/new"
    echo ""
    echo "   タイトル: Max Plan テスト"
    echo "   本文: テスト用Issue"
    echo ""
    echo "3. 作成したIssueに以下をコメント:"
    echo ""
    echo "   @claude"
    echo "   Max Planで動作確認です。正常に応答してください。"
    echo ""
    echo -e "${GREEN}🎉 すべての設定が完了しました！${NC}"
else
    echo ""
    echo -e "${RED}❌ プッシュに失敗しました${NC}"
    echo "トークンの権限を確認してください"
fi

# セキュリティのため、トークンを含むURLをリセット
echo ""
echo -e "${YELLOW}セキュリティのため、トークンを含むURLをリセットしています...${NC}"
git remote set-url origin https://github.com/RyotaKuzuya/webai-search-service.git
echo -e "${GREEN}✓ 完了${NC}"