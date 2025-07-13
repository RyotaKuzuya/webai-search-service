#!/bin/bash

echo "🔐 Claude Max Plan - 3つのトークン設定"
echo "====================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# credentials.jsonから値を取得
CREDS_FILE="/home/ubuntu/.claude/.credentials.json"

if [ -f "$CREDS_FILE" ]; then
    ACCESS_TOKEN=$(cat "$CREDS_FILE" | jq -r '.claudeAiOauth.accessToken')
    REFRESH_TOKEN=$(cat "$CREDS_FILE" | jq -r '.claudeAiOauth.refreshToken')
    EXPIRES_AT=$(cat "$CREDS_FILE" | jq -r '.claudeAiOauth.expiresAt')
    
    echo -e "${GREEN}✅ 認証情報が見つかりました！${NC}"
    echo ""
    
    echo -e "${YELLOW}Zennの記事によると、以下の3つのシークレットが必要です：${NC}"
    echo ""
    
    echo -e "${BLUE}1. CLAUDE_ACCESS_TOKEN${NC}"
    echo "=== コピー用 ==="
    echo "$ACCESS_TOKEN"
    echo "=== ここまで ==="
    echo ""
    
    echo -e "${BLUE}2. CLAUDE_REFRESH_TOKEN${NC}"
    echo "=== コピー用 ==="
    echo "$REFRESH_TOKEN"
    echo "=== ここまで ==="
    echo ""
    
    echo -e "${BLUE}3. CLAUDE_EXPIRES_AT${NC}"
    echo "=== コピー用 ==="
    echo "$EXPIRES_AT"
    echo "=== ここまで ==="
    echo ""
    
    echo -e "${RED}重要：GitHub Secretsに3つすべて設定してください${NC}"
    echo ""
    echo "設定手順："
    echo "1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
    echo ""
    echo "2. 以下の3つのシークレットを作成または更新："
    echo "   - Name: CLAUDE_ACCESS_TOKEN"
    echo "     Value: 上記のアクセストークン"
    echo ""
    echo "   - Name: CLAUDE_REFRESH_TOKEN"
    echo "     Value: 上記のリフレッシュトークン"
    echo ""
    echo "   - Name: CLAUDE_EXPIRES_AT"
    echo "     Value: 上記の有効期限（数値）"
    echo ""
    echo "3. すべて設定後、Issueで @claude メンションしてテスト"
    
else
    echo -e "${RED}❌ 認証情報ファイルが見つかりません${NC}"
    echo "場所: $CREDS_FILE"
fi