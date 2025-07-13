#!/bin/bash

echo "🔐 非対話型環境でのClaude認証"
echo "============================"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}問題：${NC}"
echo "SSH環境では対話型のClaude認証コマンドは動作しません"
echo ""

echo -e "${GREEN}解決方法：${NC}"
echo ""

echo -e "${YELLOW}オプション1: ローカルマシンで認証${NC}"
echo "1. ローカルマシン（Mac/Linux/Windows）で実行:"
echo "   curl -fsSL https://cli.claude.ai/install.sh | sh"
echo "   claude auth"
echo ""
echo "2. 認証完了後、トークンを取得:"
echo "   cat ~/.config/claude/claude_config.json | jq -r '.oauth_token'"
echo ""
echo "3. 取得したトークンをGitHub Secretsに登録"
echo ""

echo -e "${YELLOW}オプション2: 既存のトークンを探す${NC}"
echo "現在のシステムでトークンを検索中..."
echo ""

# トークンを探す
LOCATIONS=(
    "$HOME/.config/claude/claude_config.json"
    "$HOME/.claude/.credentials.json"
    "$HOME/.claude/credentials.json"
    "/home/ubuntu/.config/claude/claude_config.json"
)

TOKEN_FOUND=false
for location in "${LOCATIONS[@]}"; do
    if [ -f "$location" ]; then
        echo "✅ 設定ファイル発見: $location"
        TOKEN=$(cat "$location" | jq -r '.oauth_token // .access_token // empty' 2>/dev/null)
        if [ -n "$TOKEN" ]; then
            echo -e "${GREEN}トークンが見つかりました！${NC}"
            TOKEN_FOUND=true
            break
        fi
    fi
done

if [ "$TOKEN_FOUND" = true ]; then
    echo ""
    echo -e "${BLUE}GitHub Secretsに登録するトークン：${NC}"
    echo ""
    echo "=== コピー用 ==="
    echo "$TOKEN"
    echo "=== ここまで ==="
    echo ""
    echo "次のステップ:"
    echo "1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
    echo "2. CLAUDE_CODE_OAUTH_TOKEN を更新"
    echo "3. 上記のトークンを貼り付け"
else
    echo ""
    echo -e "${YELLOW}オプション3: Web UIから認証${NC}"
    echo "1. https://claude.ai にアクセス"
    echo "2. ログイン"
    echo "3. 開発者ツール（F12）を開く"
    echo "4. Application > Cookies > claude.ai"
    echo "5. sessionKey の値を確認"
    echo ""
    echo "※ この方法は公式ではないため推奨されません"
fi

echo ""
echo -e "${BLUE}推奨事項：${NC}"
echo "ローカルマシンで claude auth を実行してトークンを取得するのが最も安全で確実です"