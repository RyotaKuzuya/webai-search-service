#!/bin/bash

echo "🔐 SSH設定を完了する"
echo "===================="
echo ""

echo "GitHubに公開鍵を登録しましたか？ (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    echo ""
    echo "SSH接続をテスト中..."
    ssh -T git@github.com
    
    echo ""
    echo "リモートURLをSSHに変更中..."
    git remote set-url origin git@github.com:RyotaKuzuya/webai-search-service.git
    
    echo ""
    echo "✅ 設定完了！"
    echo ""
    echo "現在のリモートURL："
    git remote -v
    
    echo ""
    echo "テストプッシュを実行しますか？ (y/n)"
    read -r push_response
    
    if [[ "$push_response" == "y" ]]; then
        echo "プッシュ中..."
        git push origin master
    fi
else
    echo ""
    echo "先にGitHubに公開鍵を登録してください："
    echo "https://github.com/settings/keys"
fi