#!/bin/bash

echo "🧪 Public リポジトリでGitHub Actionsをテスト"
echo "=========================================="
echo ""

GITHUB_TOKEN="[REMOVED]"
OWNER="RyotaKuzuya"
REPO="webai-search-service"

# テスト用Issueを作成
echo "📝 テスト用Issueを作成中..."

ISSUE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{
    "title": "🎉 Public化成功！GitHub Actions無料テスト",
    "body": "リポジトリがPublicになりました！\n\nGitHub Actionsが無料で動作するかテストします。",
    "labels": ["test", "celebration"]
  }')

ISSUE_NUMBER=$(echo $ISSUE_RESPONSE | jq -r '.number')
ISSUE_URL=$(echo $ISSUE_RESPONSE | jq -r '.html_url')

echo "✅ Issue #$ISSUE_NUMBER を作成しました"
echo "URL: $ISSUE_URL"
echo ""

sleep 2

# @claudeメンションでテスト
echo "🤖 @claudeメンションでテスト..."

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/comments \
  -d '{
    "body": "@claude\n\nこんにちは！リポジトリがPublicになりました。\nGitHub Actionsが無料で動作することを確認してください。\n\n以下を教えてください：\n1. このリポジトリの概要\n2. 主な機能\n3. 改善提案"
  }' > /dev/null

echo "✅ @claudeメンションを投稿しました"
echo ""
echo "📊 確認事項："
echo "1. GitHub Actions: https://github.com/$OWNER/$REPO/actions"
echo "2. Issue: $ISSUE_URL"
echo ""
echo "🎉 すべて完了しました！"
echo ""
echo "リポジトリは現在Publicで、GitHub Actionsは無料で使用できます。"