#!/bin/bash

echo "🔐 Claude OAuth 直接認証"
echo "======================="
echo ""

# 方法1: 既存のトークンを探す
echo "方法1: 既存のトークンを確認"
echo ""

# 可能な場所をチェック
LOCATIONS=(
    "$HOME/.config/claude/claude_config.json"
    "$HOME/.claude/.credentials.json"
    "$HOME/.claude/credentials.json"
)

TOKEN_FOUND=false
for location in "${LOCATIONS[@]}"; do
    if [ -f "$location" ]; then
        echo "✅ 設定ファイルが見つかりました: $location"
        TOKEN=$(cat "$location" | jq -r '.oauth_token // .access_token // empty' 2>/dev/null)
        if [ -n "$TOKEN" ]; then
            echo "トークンが見つかりました!"
            TOKEN_FOUND=true
            break
        fi
    fi
done

if [ "$TOKEN_FOUND" = true ]; then
    echo ""
    echo "📋 GitHub Secretsに登録するトークン:"
    echo ""
    echo "=== コピー用 ==="
    echo "$TOKEN"
    echo "=== ここまで ==="
    echo ""
    echo "1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
    echo "2. CLAUDE_CODE_OAUTH_TOKEN を更新"
    echo "3. 上記のトークンを貼り付け"
else
    echo ""
    echo "方法2: 新しいトークンを生成"
    echo ""
    echo "別のターミナルまたはローカルマシンで実行:"
    echo ""
    echo "1. Claude CLIをインストール:"
    echo "   curl -fsSL https://cli.claude.ai/install.sh | sh"
    echo ""
    echo "2. 認証:"
    echo "   claude auth"
    echo ""
    echo "3. トークンを確認:"
    echo "   - Ubuntu: cat ~/.config/claude/claude_config.json"
    echo "   - macOS: security find-generic-password -a claude -s claude -w"
    echo ""
    echo "4. トークンをGitHub Secretsに登録"
fi

echo ""
echo "方法3: APIキーを使用（代替案）"
echo ""
echo "Claude Max PlanのOAuthが動作しない場合:"
echo "1. https://console.anthropic.com でAPIキーを作成"
echo "2. GitHub Secretsに ANTHROPIC_API_KEY として登録"
echo "3. ワークフローを更新して anthropic_api_key を使用"
echo ""
echo "注意: APIキーは従量課金です"