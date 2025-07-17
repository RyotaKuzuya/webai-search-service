#!/bin/bash

echo "🔧 HTTP 500エラー修正中..."
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}1. データベース接続確認${NC}"
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('/mnt/external-hdd/webai-data/db/webai.db')
    print('✅ データベース接続OK')
    conn.close()
except Exception as e:
    print(f'❌ データベースエラー: {e}')
"

echo ""
echo -e "${YELLOW}2. プロセス確認${NC}"
if pgrep -f "app.py" > /dev/null; then
    echo "✅ app.pyは実行中"
else
    echo "❌ app.pyが実行されていません"
fi

echo ""
echo -e "${YELLOW}3. ログファイル確認${NC}"
if [ -f "/mnt/external-hdd/webai-data/logs/app.log" ]; then
    echo "最新のエラー:"
    tail -10 /mnt/external-hdd/webai-data/logs/app.log | grep -i error || echo "エラーログなし"
else
    echo "ログファイルが見つかりません"
fi

echo ""
echo -e "${YELLOW}4. サービス再起動${NC}"
echo "app.pyを再起動しますか？ (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    echo "既存のプロセスを停止中..."
    pkill -f "app.py"
    sleep 2
    
    echo "app.pyを起動中..."
    cd /home/ubuntu/webai
    nohup python3 app.py > /mnt/external-hdd/webai-data/logs/app.log 2>&1 &
    sleep 3
    
    if pgrep -f "app.py" > /dev/null; then
        echo -e "${GREEN}✅ app.pyが正常に起動しました${NC}"
    else
        echo -e "${RED}❌ app.pyの起動に失敗しました${NC}"
    fi
fi