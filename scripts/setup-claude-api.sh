#!/bin/bash

# WebAI Claude Setup Script

set -e

echo "=== WebAI Claude セットアップ ==="
echo

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo "エラー: claudeコマンドが見つかりません。"
    echo ""
    echo "Claude Codeをインストールしてください："
    echo "  npm install -g claude-code"
    echo ""
    echo "または、既にインストール済みの場合は、パスを確認してください。"
    exit 1
fi

echo "✓ Claudeコマンドが見つかりました: $(which claude)"
echo

# Check Claude authentication
echo "Claude認証状態を確認中..."
if claude --version &> /dev/null; then
    echo "✓ Claudeは認証済みです"
else
    echo "警告: Claude認証が必要な場合があります"
    echo ""
    echo "認証が必要な場合は、以下の手順に従ってください："
    echo "1. 'claude login' コマンドを実行"
    echo "2. 表示されるURLをブラウザで開く"
    echo "3. Anthropicアカウントでログイン"
    echo "4. 認証コードを入力"
fi

echo
echo "=== セットアップ完了 ==="
echo
echo "WebAIアプリケーションを起動するには："
echo "  cd /home/ubuntu/webai"
echo "  ./start-webai.sh"