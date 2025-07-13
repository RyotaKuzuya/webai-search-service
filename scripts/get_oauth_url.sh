#!/bin/bash

echo "🔐 Claude OAuth 認証URL取得"
echo "=========================="
echo ""

# OAuth認証のURL生成
CLIENT_ID="9d1c250a-e61b-44d9-88ed-5944d1962f5e"
REDIRECT_URI="http://localhost:3003/callback"
STATE=$(openssl rand -hex 16)
CODE_VERIFIER=$(openssl rand -base64 48 | tr -d "=+/" | cut -c 1-128)
CODE_CHALLENGE=$(echo -n "$CODE_VERIFIER" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')

AUTH_URL="https://auth.claude.ai/oauth/authorize?client_id=${CLIENT_ID}&response_type=code&redirect_uri=${REDIRECT_URI}&scope=claude_code_all&state=${STATE}&code_challenge=${CODE_CHALLENGE}&code_challenge_method=S256"

echo "1. 以下のURLをブラウザで開いてください:"
echo ""
echo "$AUTH_URL"
echo ""
echo "2. Anthropicアカウントでログイン"
echo ""
echo "3. 認証を承認"
echo ""
echo "4. リダイレクト後のURLから 'code=' の後の文字列をコピー"
echo "   例: http://localhost:3003/callback?code=XXXXXXXX"
echo ""
echo "5. 認証コードを入力してください:"
read -r AUTH_CODE

if [ -z "$AUTH_CODE" ]; then
    echo "❌ 認証コードが入力されていません"
    exit 1
fi

echo ""
echo "✅ 認証コードを受け取りました"
echo ""

# トークン交換
echo "トークンを取得中..."

TOKEN_RESPONSE=$(curl -s -X POST "https://auth.claude.ai/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=$AUTH_CODE" \
  -d "redirect_uri=$REDIRECT_URI" \
  -d "client_id=$CLIENT_ID" \
  -d "code_verifier=$CODE_VERIFIER")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token // empty')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.refresh_token // empty')

if [ -n "$ACCESS_TOKEN" ]; then
    echo "✅ トークン取得成功!"
    echo ""
    
    # 設定ファイルを作成
    mkdir -p ~/.config/claude
    cat > ~/.config/claude/claude_config.json << EOF
{
  "oauth_token": "$ACCESS_TOKEN",
  "refresh_token": "$REFRESH_TOKEN",
  "expires_at": "$(date -d '+7 days' -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    echo "設定ファイルを作成しました: ~/.config/claude/claude_config.json"
    echo ""
    echo "📋 GitHub Secretsに登録するトークン:"
    echo ""
    echo "=== コピー用 ==="
    echo "$ACCESS_TOKEN"
    echo "=== ここまで ==="
    echo ""
    echo "次のステップ:"
    echo "1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
    echo "2. CLAUDE_CODE_OAUTH_TOKEN を更新"
    echo "3. 上記のトークンを貼り付け"
else
    echo "❌ トークン取得に失敗しました"
    echo "レスポンス: $TOKEN_RESPONSE"
fi