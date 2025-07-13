#!/bin/bash

echo "🔐 Git永続的認証設定（トークン不要）"
echo "===================================="
echo ""

echo "以下の方法でGitの認証を設定できます："
echo ""

echo "方法1: SSH鍵を使用（最も安全）"
echo "1. SSH鍵を生成: ssh-keygen -t ed25519 -C 'your_email@example.com'"
echo "2. 公開鍵をGitHubに登録: https://github.com/settings/keys"
echo "3. リモートURLをSSHに変更: git remote set-url origin git@github.com:RyotaKuzuya/webai-search-service.git"
echo ""

echo "方法2: GitHub CLIを使用"
echo "1. インストール: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
echo "2. 認証: gh auth login"
echo "3. 以降は自動認証"
echo ""

echo "方法3: Git Credential Helperを設定済み"
echo "次回push時にユーザー名とトークンを入力すれば保存されます"
echo ""

echo "現在の設定:"
git config --global credential.helper
echo ""
echo "トークンを使わずにGitを使いたい場合は、SSH鍵の設定を推奨します。"