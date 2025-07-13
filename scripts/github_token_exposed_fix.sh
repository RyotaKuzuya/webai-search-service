#!/bin/bash

echo "⚠️  GitHub個人アクセストークン漏洩の対処"
echo "========================================="
echo ""

# カラー設定
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}警告: GitHubがコミット内でトークンを検出しました${NC}"
echo ""

# 漏洩した可能性のあるトークンを探す
echo -e "${YELLOW}最近のコミットでトークンを確認中...${NC}"
echo ""

# 最近のコミットログを確認
git log --oneline -n 10

echo ""
echo -e "${BLUE}漏洩したトークンの可能性:${NC}"
echo "[REMOVED]"
echo ""

echo -e "${RED}緊急対処手順:${NC}"
echo ""

echo "1. 🚨 漏洩したトークンを直ちに無効化"
echo "   https://github.com/settings/tokens"
echo "   - 該当トークンの 'Delete' をクリック"
echo ""

echo "2. 🔑 新しいトークンを作成（必要な場合）"
echo "   https://github.com/settings/tokens/new"
echo "   - 最小限の権限のみ付与"
echo "   - 有効期限を短く設定"
echo ""

echo "3. 🧹 コミット履歴から削除"
echo "   以下のコマンドを実行してトークンを履歴から削除:"
echo ""
echo "   # BFG Repo-Cleanerを使用（推奨）"
echo "   java -jar bfg.jar --replace-text passwords.txt"
echo ""
echo "   # または git filter-branch（複雑）"
echo "   git filter-branch --force --index-filter \\"
echo "   'git rm --cached --ignore-unmatch path/to/file' \\"
echo "   --prune-empty --tag-name-filter cat -- --all"
echo ""

echo "4. 📤 強制プッシュ"
echo "   git push --force --all"
echo "   git push --force --tags"
echo ""

echo -e "${GREEN}予防策:${NC}"
echo "- .gitignore に秘密情報を追加"
echo "- 環境変数やGitHub Secretsを使用"
echo "- git-secretsツールを導入"
echo ""

echo -e "${YELLOW}重要: トークンは既にGitHubによって自動的に無効化されている可能性があります${NC}"