#!/bin/bash

# Vercel用デプロイメントスクリプト
# 無料でWebAIを公開する

echo "========================================"
echo "WebAI Vercel デプロイメント"
echo "========================================"
echo ""

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vercel CLIの確認
check_vercel() {
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Vercel CLIをインストール中...${NC}"
        npm install -g vercel
    fi
}

# プロジェクト準備
prepare_project() {
    echo -e "${YELLOW}プロジェクトを準備中...${NC}"
    
    # Vercel用のエントリーポイント作成
    cat > api/index.py << 'EOF'
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

# Vercel serverless function handler
def handler(request, response):
    # Setup environment
    os.environ['MOCK_MODE'] = 'true'
    os.environ['ADMIN_USERNAME'] = 'admin'
    os.environ['ADMIN_PASSWORD'] = 'demo123'
    
    # Process request
    with app.test_request_context(
        path=request.path,
        method=request.method,
        headers=request.headers,
        data=request.body
    ):
        try:
            # Get Flask response
            flask_response = app.full_dispatch_request()
            
            # Convert to Vercel response
            response.status_code = flask_response.status_code
            response.headers = dict(flask_response.headers)
            response.body = flask_response.get_data()
            
        except Exception as e:
            response.status_code = 500
            response.body = str(e)

app = handler
EOF

    # requirements.txt作成
    cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-SocketIO==5.3.4
python-socketio==5.9.0
python-dotenv==1.0.0
requests==2.31.0
EOF

    # publicディレクトリ作成
    mkdir -p public
    cp -r frontend/* public/ 2>/dev/null || true
    
    echo -e "${GREEN}✓ プロジェクト準備完了${NC}"
}

# Vercelデプロイ
deploy_to_vercel() {
    echo -e "${YELLOW}Vercelにデプロイ中...${NC}"
    
    # Vercel login
    echo -e "${BLUE}Vercelアカウントにログインしてください:${NC}"
    vercel login
    
    # Deploy
    echo -e "${YELLOW}デプロイを開始します...${NC}"
    vercel --prod
    
    echo -e "${GREEN}✓ デプロイ完了！${NC}"
}

# クリーンアップ
cleanup() {
    echo -e "${YELLOW}一時ファイルをクリーンアップ中...${NC}"
    rm -rf api/
    rm -f requirements.txt
    rm -rf public/
}

# メイン処理
main() {
    echo -e "${BLUE}このスクリプトはWebAIをVercelに無料でデプロイします${NC}"
    echo ""
    echo "必要なもの:"
    echo "- Vercelアカウント（無料）"
    echo "- Node.js（npm）"
    echo ""
    
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    
    # 実行
    check_vercel
    prepare_project
    deploy_to_vercel
    
    # 完了メッセージ
    echo ""
    echo -e "${GREEN}========================================"
    echo "デプロイ完了！"
    echo "========================================"
    echo ""
    echo "アプリケーションURL:"
    echo "https://webai-*.vercel.app"
    echo ""
    echo "ログイン情報:"
    echo "  ユーザー名: admin"
    echo "  パスワード: demo123"
    echo ""
    echo "注意: Vercelは静的サイトとサーバーレス関数に最適化されているため、"
    echo "WebSocketは使用できません。基本的なチャット機能のみ利用可能です。"
    echo -e "${NC}"
    
    # クリーンアップ確認
    read -p "一時ファイルを削除しますか？ (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        cleanup
    fi
}

# トラップ設定
trap cleanup EXIT

# 実行
main