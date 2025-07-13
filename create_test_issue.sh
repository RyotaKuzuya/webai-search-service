#!/bin/bash

echo "📝 GitHub Issue作成スクリプト"
echo "=============================="
echo ""

# GitHubトークンの確認
if [ -z "$GITHUB_TOKEN" ]; then
    echo "GitHubトークンを環境変数に設定してください："
    echo "export GITHUB_TOKEN=[REMOVED]"
    echo ""
    echo "または、直接トークンを使用："
    GITHUB_TOKEN="[REMOVED]"
fi

OWNER="RyotaKuzuya"
REPO="webai-search-service"

# Issue作成
echo "🔸 Issue作成中..."
ISSUE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{
    "title": "GitHub Actions動作テスト",
    "body": "GitHub Actionsが正しく動作するかテストします。\n\nこのIssueにコメントを追加してワークフローがトリガーされるか確認します。",
    "labels": ["test"]
  }')

ISSUE_NUMBER=$(echo $ISSUE_RESPONSE | jq -r '.number')
ISSUE_URL=$(echo $ISSUE_RESPONSE | jq -r '.html_url')

if [ "$ISSUE_NUMBER" = "null" ]; then
    echo "❌ Issue作成に失敗しました"
    echo "レスポンス: $ISSUE_RESPONSE"
    exit 1
fi

echo "✅ Issue #$ISSUE_NUMBER を作成しました"
echo "URL: $ISSUE_URL"
echo ""

# 少し待つ
sleep 2

# コメント1: @test
echo "🔸 コメント1を投稿中 (@test)..."
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/comments \
  -d '{
    "body": "@test"
  }' > /dev/null

echo "✅ @test コメントを投稿しました"
sleep 3

# コメント2: @claude
echo "🔸 コメント2を投稿中 (@claude)..."
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/comments \
  -d '{
    "body": "@claude こんにちは！動作確認です。"
  }' > /dev/null

echo "✅ @claude コメントを投稿しました"
echo ""

echo "📊 確認事項："
echo "1. GitHub Actions: https://github.com/$OWNER/$REPO/actions"
echo "2. Issue: $ISSUE_URL"
echo ""
echo "ワークフローがトリガーされているか確認してください。"