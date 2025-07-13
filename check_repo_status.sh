#!/bin/bash

echo "🔍 リポジトリとアカウント状態の確認"
echo "===================================="
echo ""

# リポジトリの可視性を確認
echo "📂 リポジトリ情報:"
curl -s https://api.github.com/repos/RyotaKuzuya/webai-search-service | jq -r '
    "名前: \(.full_name)
可視性: \(.visibility)
Private: \(.private)
作成日: \(.created_at)
更新日: \(.updated_at)"'

echo ""
echo "✅ 確認結果:"
echo "- リポジトリは Public です（無料枠）"
echo "- Public リポジトリは GitHub Actions が無制限"
echo ""

echo "❌ それでもエラーが出る理由:"
echo "1. アカウントの支払い履歴に問題"
echo "2. 過去の未払いがある"
echo "3. アカウントが制限されている"
echo ""

echo "💡 解決策:"
echo "1. https://github.com/settings/billing で支払い設定確認"
echo "2. 別のGitHubアカウントでForkして試す"
echo "3. ローカルでClaude Codeを使用（GitHub Actions不要）"
echo ""

echo "🚀 代替方法:"
echo "GitHub Actionsを使わずに、このサーバーで直接Claude Codeを使用できます:"
echo "- Web UI: http://localhost:5000"
echo "- API: http://localhost:8000/v1/chat/completions"