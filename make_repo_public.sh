#!/bin/bash

echo "🔄 リポジトリをPublicに変更中..."
echo ""

# GitHubトークン（既存のものを使用）
GITHUB_TOKEN="[REMOVED]"
OWNER="RyotaKuzuya"
REPO="webai-search-service"

# リポジトリをPublicに変更
echo "📢 リポジトリをPublicに変更..."
response=$(curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO \
  -d '{"private": false}')

# 結果を確認
is_private=$(echo $response | jq -r '.private')

if [ "$is_private" = "false" ]; then
    echo "✅ リポジトリが正常にPublicに変更されました！"
    echo ""
    echo "🎉 GitHub Actionsが無料で使用できるようになりました！"
    echo ""
    echo "確認URL: https://github.com/$OWNER/$REPO"
else
    echo "❌ エラーが発生しました"
    echo "$response" | jq '.'
fi