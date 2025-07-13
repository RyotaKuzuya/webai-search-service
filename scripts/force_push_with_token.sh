#!/bin/bash

echo "🔐 Force Push実行ガイド"
echo "======================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}✅ Git履歴のクリーンアップ完了${NC}"
echo "- すべてのトークンが履歴から削除されました"
echo "- ローカルリポジトリはクリーンです"
echo ""

echo -e "${YELLOW}⚠️  リモートリポジトリへの反映が必要です${NC}"
echo ""

echo -e "${BLUE}オプション1: GitHub CLIを使用（推奨）${NC}"
echo "gh auth status でログイン状態を確認してから:"
echo ""
echo "gh auth login"
echo "git push --force --all origin"
echo "git push --force --tags origin"
echo ""

echo -e "${BLUE}オプション2: 個人アクセストークンを使用${NC}"
echo "1. 新しいトークンを作成:"
echo "   https://github.com/settings/tokens/new"
echo "   - Expiration: 7 days"
echo "   - Scopes: repo (Full control)"
echo ""
echo "2. 以下を実行（トークンを置き換え）:"
echo ""
cat << 'EOF'
# トークンを環境変数に設定
export GITHUB_TOKEN="ghp_YOUR_NEW_TOKEN_HERE"

# pushを実行
git push --force --all https://$GITHUB_TOKEN@github.com/RyotaKuzuya/webai-search-service.git
git push --force --tags https://$GITHUB_TOKEN@github.com/RyotaKuzuya/webai-search-service.git

# トークンをクリア
unset GITHUB_TOKEN
EOF
echo ""

echo -e "${BLUE}オプション3: パスワード認証${NC}"
echo "git push --force --all origin"
echo "# ユーザー名とパスワードを入力"
echo ""

echo -e "${RED}重要な注意事項:${NC}"
echo "- Force pushは履歴を書き換えます"
echo "- 他の開発者に影響する可能性があります"
echo "- 実行前に確認してください"
echo ""

echo -e "${GREEN}完了後の確認:${NC}"
echo "1. GitHubのWebUIで履歴を確認"
echo "2. セキュリティ警告が消えていることを確認"
echo "3. 使用した一時トークンを削除"