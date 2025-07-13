#!/bin/bash

echo "🔐 Git認証トークン設定"
echo "======================"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}重要: トークンを安全に管理してください${NC}"
echo ""

echo -e "${BLUE}オプション1: Git Credential Manager（推奨）${NC}"
echo "git config --global credential.helper store"
echo "# 次回のpush時にユーザー名とトークンを入力"
echo ""

echo -e "${BLUE}オプション2: リモートURLにトークンを埋め込む${NC}"
echo "# 注意: この方法はトークンがgit configに保存されます"
echo 'git remote set-url origin https://USERNAME:TOKEN@github.com/RyotaKuzuya/webai-search-service.git'
echo ""

echo -e "${BLUE}オプション3: 環境変数を使用（セッション限定）${NC}"
echo 'export GITHUB_TOKEN="your_token_here"'
echo 'git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"'
echo ""

echo -e "${GREEN}推奨設定:${NC}"
echo "1. Git Credential Helperを設定:"
echo "   git config --global credential.helper store"
echo ""
echo "2. 初回push時に認証情報を入力:"
echo "   Username: RyotaKuzuya"
echo "   Password: [your-github-token]"
echo ""
echo "3. 以降は自動的に認証されます"

# 現在の設定を確認
echo ""
echo -e "${YELLOW}現在のGit設定:${NC}"
git config --global credential.helper || echo "credential.helper: 未設定"