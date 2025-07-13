#!/bin/bash

echo "🚀 クイックプッシュスクリプト"
echo "============================"
echo ""

if [ -z "$1" ]; then
    echo "使用方法: ./quick_push.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "例: ./quick_push.sh ghp_xxxxxxxxxxxxx"
    echo ""
    echo "GitHubトークンの作成:"
    echo "1. https://github.com/settings/tokens/new"
    echo "2. Scopes: ☑ repo"
    echo "3. Generate token"
    exit 1
fi

GITHUB_TOKEN=$1

echo "📤 GitHubにプッシュ中..."
git remote set-url origin https://${GITHUB_TOKEN}@github.com/RyotaKuzuya/webai-search-service.git

if git push origin master; then
    echo ""
    echo "✅ プッシュ成功！"
    echo ""
    echo "📋 次のステップ:"
    echo ""
    echo "1. Actions確認: https://github.com/RyotaKuzuya/webai-search-service/actions"
    echo ""
    echo "2. 新しいIssue作成: https://github.com/RyotaKuzuya/webai-search-service/issues/new"
    echo "   タイトル: Max Plan Test"
    echo "   本文: Testing Max Plan support"
    echo ""
    echo "3. Issueにコメント:"
    echo "   @claude"
    echo "   Max Plan (v1.0.44+) の動作テストです。応答してください。"
    echo ""
    echo "🎉 完了！Max Plan + GitHub Actions = 無料！"
else
    echo ""
    echo "❌ プッシュ失敗"
fi

# セキュリティのためURLをリセット
git remote set-url origin https://github.com/RyotaKuzuya/webai-search-service.git
echo ""
echo "🔒 セキュリティのため、トークンを削除しました"