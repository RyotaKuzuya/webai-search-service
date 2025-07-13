#!/bin/bash

echo "📤 最終プッシュ"
echo "==============="
echo ""

echo "✅ 完了した作業:"
echo "- 56個のMDファイル削除（README.md以外）"
echo "- セキュリティチェック完了（ID/PWは環境変数）"
echo "- ローカルコミット済み"
echo ""

echo "🔐 プッシュに必要な認証:"
echo "先ほど使用した一時トークンを再度使用するか、"
echo "新しいトークンを作成してください"
echo ""

echo "コマンド例:"
echo 'export GITHUB_TOKEN="ghp_YOUR_TOKEN"'
echo 'git push https://$GITHUB_TOKEN@github.com/RyotaKuzuya/webai-search-service.git master'
echo 'unset GITHUB_TOKEN'