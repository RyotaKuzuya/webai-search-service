#!/bin/bash

echo "🔒 セキュリティクリーンアップ実行中..."
echo ""

# 機密ファイルの削除
echo "1. 機密ファイルを削除..."
rm -rf claude-config/
rm -f .env
rm -f *.json
rm -rf certbot/
rm -f *token*.py
rm -f *secret*.py

# BFG Repo-Cleanerをダウンロード
echo ""
echo "2. BFG Repo-Cleanerをダウンロード..."
wget -q https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Git履歴から機密情報を削除
echo ""
echo "3. Git履歴から機密情報を削除..."

# 特定のファイルを履歴から削除
java -jar bfg-1.14.0.jar --delete-files claude_config.json .
java -jar bfg-1.14.0.jar --delete-files .env .
java -jar bfg-1.14.0.jar --delete-files "*.pem" .
java -jar bfg-1.14.0.jar --delete-files "*.key" .

# 機密文字列を置換
echo ""
echo "4. 機密文字列を置換..."

# トークンパターンを削除
java -jar bfg-1.14.0.jar --replace-text <(echo "[REMOVED]==>REMOVED") .
java -jar bfg-1.14.0.jar --replace-text <(echo "sk-ant-oat01-*==>REMOVED") .
java -jar bfg-1.14.0.jar --replace-text <(echo "sk-ant-ort01-*==>REMOVED") .
java -jar bfg-1.14.0.jar --replace-text <(echo "WebAI@2024SecurePass!==>REMOVED") .

# Git履歴を更新
echo ""
echo "5. Git履歴を更新..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "⚠️  重要: 以下のコマンドで強制プッシュが必要です:"
echo "git push --force origin master"
echo ""
echo "✅ クリーンアップ完了！"