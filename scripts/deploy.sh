#!/bin/bash

# WebAI Service Deployment Script

set -e

echo "=== WebAI Service デプロイメントスクリプト ==="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "エラー: このスクリプトはrootユーザーで実行しないでください"
   exit 1
fi

# Function to check if service is running
check_service() {
    if systemctl is-active --quiet $1; then
        echo "✓ $1 is running"
        return 0
    else
        echo "✗ $1 is not running"
        return 1
    fi
}

# 1. Backup existing Nginx configuration
echo "1. 既存のNginx設定をバックアップ中..."
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
fi

# 2. Setup Claude Code
echo
echo "2. Claude Codeをセットアップ中..."
./setup-claude-api.sh

# 3. Install WebAI dependencies
echo
echo "3. WebAI依存関係をインストール中..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup environment file
echo
echo "4. 環境設定ファイルをセットアップ中..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   警告: .envファイルを編集して適切な値を設定してください"
    echo "   特に以下の値を設定してください:"
    echo "   - SECRET_KEY"
    echo "   - ADMIN_PASSWORD"
    echo "   - ANTHROPIC_API_KEY"
fi

# 5. Setup Nginx
echo
echo "5. Nginxを設定中..."
sudo cp nginx/conf.d/webai.conf /etc/nginx/sites-available/webai
sudo ln -sf /etc/nginx/sites-available/webai /etc/nginx/sites-enabled/webai
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "   Nginx設定をテスト中..."
sudo nginx -t

# 6. Setup systemd services
echo
echo "6. systemdサービスを設定中..."

# Claude認証の確認
echo "   Claude認証を確認中..."
if ! claude --version &> /dev/null; then
    echo "   警告: Claude認証が必要です。'claude login'を実行してください。"
fi

sudo systemctl daemon-reload

# WebAI service
cat << EOF | sudo tee /etc/systemd/system/webai.service
[Unit]
Description=WebAI Search Service
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/webai
Environment="PATH=/home/ubuntu/webai/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="CLAUDE_EXECUTABLE=claude"
EnvironmentFile=/home/ubuntu/webai/.env
ExecStart=/home/ubuntu/webai/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 7. Start services
echo
echo "7. サービスを起動中..."

# Enable and start services
sudo systemctl enable webai
sudo systemctl restart webai
sudo systemctl restart nginx

# 8. Check services status
echo
echo "8. サービスステータスを確認中..."
check_service nginx
check_service webai

echo
echo "=== デプロイメント完了 ==="
echo
echo "次のステップ:"
echo "1. .envファイルを編集して必要な環境変数を設定"
echo "2. sudo systemctl restart claude-api webai でサービスを再起動"
echo "3. https://your-domain.com でアクセス確認"
echo
echo "ログの確認:"
echo "- sudo journalctl -u webai -f"
echo "- sudo tail -f /var/log/nginx/error.log"