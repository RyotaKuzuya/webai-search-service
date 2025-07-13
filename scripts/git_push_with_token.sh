#!/bin/bash

echo "🚀 Gitプッシュ実行"
echo "=================="
echo ""

# 引数からトークンを受け取る
if [ -z "$1" ]; then
    echo "使用方法: ./git_push_with_token.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "例: ./git_push_with_token.sh ghp_xxxxxxxxxxxxx"
    exit 1
fi

TOKEN=$1

echo "プッシュを実行中..."
git push https://RyotaKuzuya:$TOKEN@github.com/RyotaKuzuya/webai-search-service.git master

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ プッシュ成功！"
    echo ""
    echo "Git Credential Helperに保存されました。"
    echo "今後は 'git push' だけで自動認証されます。"
else
    echo ""
    echo "❌ プッシュ失敗"
    echo "トークンと権限を確認してください。"
fi