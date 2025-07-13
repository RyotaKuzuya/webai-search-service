#!/bin/bash

echo "✅ Claude OAuthトークンが見つかりました！"
echo "=========================================="
echo ""

# トークンを取得
TOKEN=$(cat /home/ubuntu/.claude/.credentials.json | jq -r '.claudeAiOauth.accessToken')

echo "トークンタイプ: Claude Max Plan OAuth Token"
echo "有効期限: $(date -d @$(($(cat /home/ubuntu/.claude/.credentials.json | jq -r '.claudeAiOauth.expiresAt')/1000)))"
echo ""

echo "📋 GitHub Secretsに登録する手順："
echo ""
echo "1. 以下のURLにアクセス:"
echo "   https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
echo ""
echo "2. CLAUDE_CODE_OAUTH_TOKEN を探す（または新規作成）"
echo ""
echo "3. 以下のトークンをコピーして貼り付け:"
echo ""
echo "=== トークン（コピー用） ==="
echo "$TOKEN"
echo "=== ここまで ==="
echo ""
echo "4. 'Update secret' または 'Add secret' をクリック"
echo ""
echo "5. 保存後、新しいIssueでテスト:"
echo "   - タイトル: OAuth Test"
echo "   - 本文に @claude と記載"
echo ""
echo "🎉 これでGitHub ActionsでClaude Max Planが使えるようになります！"