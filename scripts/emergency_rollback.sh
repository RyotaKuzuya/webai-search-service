#!/bin/bash

echo "🚨 緊急ロールバック実行"
echo "======================="
echo ""

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}HDD移行を元に戻します${NC}"
echo ""

# 1. app.pyを停止
echo "1. app.pyを停止中..."
pkill -f "app.py"
sleep 2

# 2. シンボリックリンクを削除して、元のファイルに戻す
echo "2. データベースを元の場所に戻す..."

# データベースのバックアップを作成
if [ -f "/mnt/external-hdd/webai-data/db/webai.db" ]; then
    cp /mnt/external-hdd/webai-data/db/webai.db /home/ubuntu/webai/webai.db.backup
    echo "✅ データベースのバックアップを作成"
fi

# シンボリックリンクを削除
rm -f /home/ubuntu/webai/webai.db

# 元のデータベースファイルに戻す
if [ -f "/home/ubuntu/webai/webai.db.backup" ]; then
    mv /home/ubuntu/webai/webai.db.backup /home/ubuntu/webai/webai.db
    echo "✅ データベースを元の場所に配置"
else
    # バックアップがない場合は外付けHDDからコピー
    if [ -f "/mnt/external-hdd/webai-data/db/webai.db" ]; then
        cp /mnt/external-hdd/webai-data/db/webai.db /home/ubuntu/webai/webai.db
        echo "✅ 外付けHDDからデータベースをコピー"
    fi
fi

# 3. config.pyを無効化（元に戻す）
echo "3. 設定ファイルを元に戻す..."
if [ -f "/home/ubuntu/webai/config.py" ]; then
    mv /home/ubuntu/webai/config.py /home/ubuntu/webai/config.py.disabled
    echo "✅ config.pyを無効化"
fi

# 4. session_manager.pyを元に戻す
echo "4. SessionManagerを元に戻す..."
sed -i '14,18d' /home/ubuntu/webai/session_manager.py
sed -i '14i\        self.db_path = db_path' /home/ubuntu/webai/session_manager.py

# 5. app.pyを再起動
echo ""
echo -e "${YELLOW}5. app.pyを再起動中...${NC}"
cd /home/ubuntu/webai
nohup python3 app.py > app.log 2>&1 &
sleep 3

if pgrep -f "app.py" > /dev/null; then
    echo -e "${GREEN}✅ app.pyが正常に起動しました${NC}"
    echo ""
    echo "ロールバック完了！"
    echo "データベースは元の場所（/home/ubuntu/webai/webai.db）に戻りました"
else
    echo -e "${RED}❌ app.pyの起動に失敗しました${NC}"
fi