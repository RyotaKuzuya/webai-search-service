#!/bin/bash

echo "🚀 WebAI全サービス起動スクリプト"
echo "================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 既存のプロセスを停止
echo -e "${YELLOW}1. 既存のプロセスを停止中...${NC}"
pkill -f "app.py"
pkill -f "simple_api.py"
sleep 2

# 2. Simple APIを起動（ポート8001）
echo -e "${YELLOW}2. Simple API起動中...${NC}"
cd /home/ubuntu/webai
python3 utils/simple_api.py > logs/simple_api.log 2>&1 &
sleep 2

if pgrep -f "simple_api.py" > /dev/null; then
    echo -e "${GREEN}✅ Simple API起動成功（ポート8001）${NC}"
else
    echo -e "${RED}❌ Simple API起動失敗${NC}"
    exit 1
fi

# 3. メインアプリケーションを起動（ポート5000）
echo -e "${YELLOW}3. WebAIアプリケーション起動中...${NC}"
python3 app.py > app.log 2>&1 &
sleep 3

if pgrep -f "app.py" > /dev/null; then
    echo -e "${GREEN}✅ WebAI起動成功（ポート5000）${NC}"
else
    echo -e "${RED}❌ WebAI起動失敗${NC}"
    exit 1
fi

# 4. 動作確認
echo ""
echo -e "${YELLOW}4. 動作確認中...${NC}"
sleep 2

# APIテスト
response=$(curl -s -X POST http://localhost:8001/chat -H "Content-Type: application/json" -d '{"message":"test"}' | jq -r '.message' 2>/dev/null)
if [ -n "$response" ]; then
    echo -e "${GREEN}✅ API動作確認OK${NC}"
else
    echo -e "${RED}❌ API応答なし${NC}"
fi

# Webサーバーテスト
if curl -s http://localhost:5000/ | grep -q "WebAI"; then
    echo -e "${GREEN}✅ Webサーバー動作確認OK${NC}"
else
    echo -e "${RED}❌ Webサーバー応答なし${NC}"
fi

echo ""
echo -e "${GREEN}🎉 全サービス起動完了！${NC}"
echo ""
echo "アクセス方法："
echo "- Web UI: http://localhost:5000"
echo "- API: http://localhost:8001/chat"
echo ""
echo "ログファイル："
echo "- app.log"
echo "- logs/simple_api.log"