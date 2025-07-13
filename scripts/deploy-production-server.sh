#!/bin/bash

# 本番サーバーへの完全自動デプロイスクリプト
# your-domain.comで本番環境を動かすための最終スクリプト

echo "=========================================="
echo "WebAI 本番サーバー 自動デプロイ"
echo "=========================================="
echo ""

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 設定
DOMAIN="your-domain.com"
EMAIL="admin@your-domain.com"
SERVER_IP=""

# サーバー情報収集
collect_server_info() {
    echo -e "${YELLOW}サーバー情報を収集中...${NC}"
    
    if [ -z "$SERVER_IP" ]; then
        read -p "サーバーのIPアドレスを入力: " SERVER_IP
    fi
    
    echo -e "${GREEN}✓ サーバーIP: $SERVER_IP${NC}"
}

# SSH接続テスト
test_ssh_connection() {
    echo -e "${YELLOW}SSH接続をテスト中...${NC}"
    
    ssh -o ConnectTimeout=5 -o BatchMode=yes root@$SERVER_IP exit 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SSH接続成功${NC}"
        SSH_USER="root"
    else
        read -p "SSHユーザー名を入力: " SSH_USER
        ssh -o ConnectTimeout=5 $SSH_USER@$SERVER_IP exit
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ SSH接続に失敗しました${NC}"
            echo "以下を確認してください:"
            echo "1. サーバーのIPアドレスが正しい"
            echo "2. SSHキーが設定されている"
            echo "3. ファイアウォールでポート22が開いている"
            exit 1
        fi
    fi
}

# リモートサーバーセットアップ
setup_remote_server() {
    echo -e "${YELLOW}リモートサーバーをセットアップ中...${NC}"
    
    # セットアップスクリプト作成
    cat > /tmp/remote_setup.sh << 'REMOTE_SCRIPT'
#!/bin/bash

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}サーバー環境を準備中...${NC}"

# システム更新
apt-get update -y
apt-get upgrade -y

# 必要なパッケージインストール
apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban

# Docker インストール
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Docker Compose インストール
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# アプリケーションディレクトリ作成
mkdir -p /opt/webai
cd /opt/webai

echo -e "${GREEN}✓ サーバー準備完了${NC}"
REMOTE_SCRIPT

    # スクリプト実行
    scp /tmp/remote_setup.sh $SSH_USER@$SERVER_IP:/tmp/
    ssh $SSH_USER@$SERVER_IP "sudo bash /tmp/remote_setup.sh"
    rm /tmp/remote_setup.sh
}

# アプリケーションデプロイ
deploy_application() {
    echo -e "${YELLOW}アプリケーションをデプロイ中...${NC}"
    
    # ファイル転送
    echo "ファイルを転送中..."
    rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
        --exclude='*.pyc' --exclude='.env' \
        ./ $SSH_USER@$SERVER_IP:/opt/webai/
    
    # リモート設定
    ssh $SSH_USER@$SERVER_IP << 'REMOTE_COMMANDS'
cd /opt/webai

# 環境変数設定
if [ ! -f .env ]; then
    cp .env.sample .env
    
    # セキュアキー生成
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-secret-key-here-please-change-this/$SECRET_KEY/" .env
    
    # ドメイン設定
    sed -i "s/DOMAIN_NAME=.*/DOMAIN_NAME=your-domain.com/" .env
    sed -i "s/LETSENCRYPT_EMAIL=.*/LETSENCRYPT_EMAIL=admin@your-domain.com/" .env
fi

# ディレクトリ作成
mkdir -p claude-config certbot/conf certbot/www logs

# 権限設定
chmod 600 .env
chmod 700 claude-config

# Dockerイメージビルド
docker-compose -f docker-compose.prod.yml build

echo "✓ アプリケーションデプロイ完了"
REMOTE_COMMANDS
}

# SSL証明書設定
setup_ssl_certificate() {
    echo -e "${YELLOW}SSL証明書を設定中...${NC}"
    
    ssh $SSH_USER@$SERVER_IP << 'REMOTE_SSL'
cd /opt/webai

# Nginx一時設定
cat > /etc/nginx/sites-available/webai-temp << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}
EOF

ln -sf /etc/nginx/sites-available/webai-temp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# SSL証明書取得
certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@your-domain.com \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d your-domain.com \
    -d www.your-domain.com

# SSL設定確認
if [ -d "/etc/letsencrypt/live/your-domain.com" ]; then
    echo "✓ SSL証明書取得成功"
    
    # certbotディレクトリにコピー
    mkdir -p /opt/webai/certbot/conf
    cp -RL /etc/letsencrypt/* /opt/webai/certbot/conf/
else
    echo "⚠ SSL証明書取得に失敗しました"
fi
REMOTE_SSL
}

# ファイアウォール設定
setup_firewall() {
    echo -e "${YELLOW}ファイアウォールを設定中...${NC}"
    
    ssh $SSH_USER@$SERVER_IP << 'REMOTE_FW'
# UFW設定
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Fail2ban設定
systemctl enable fail2ban
systemctl start fail2ban

echo "✓ ファイアウォール設定完了"
REMOTE_FW
}

# サービス起動
start_services() {
    echo -e "${YELLOW}サービスを起動中...${NC}"
    
    ssh $SSH_USER@$SERVER_IP << 'REMOTE_START'
cd /opt/webai

# Docker Compose起動
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 起動確認
sleep 10
docker-compose -f docker-compose.prod.yml ps

# ヘルスチェック
curl -s -o /dev/null -w "%{http_code}" http://localhost
if [ $? -eq 0 ]; then
    echo "✓ サービス起動成功"
else
    echo "⚠ サービス起動に問題があります"
    docker-compose -f docker-compose.prod.yml logs --tail=50
fi
REMOTE_START
}

# DNS設定確認
check_dns() {
    echo -e "${YELLOW}DNS設定を確認中...${NC}"
    
    RESOLVED_IP=$(dig +short $DOMAIN @8.8.8.8)
    if [ "$RESOLVED_IP" = "$SERVER_IP" ]; then
        echo -e "${GREEN}✓ DNS設定正常: $DOMAIN → $SERVER_IP${NC}"
    else
        echo -e "${RED}⚠ DNS設定を確認してください${NC}"
        echo "現在の設定: $DOMAIN → $RESOLVED_IP"
        echo "期待される設定: $DOMAIN → $SERVER_IP"
        echo ""
        echo "ドメインレジストラで以下の設定を行ってください:"
        echo "Aレコード: @ → $SERVER_IP"
        echo "Aレコード: www → $SERVER_IP"
    fi
}

# メイン処理
main() {
    echo -e "${BLUE}WebAIを本番サーバー（your-domain.com）にデプロイします${NC}"
    echo ""
    
    # サーバー情報収集
    collect_server_info
    
    # SSH接続確認
    test_ssh_connection
    
    echo ""
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    
    # デプロイ実行
    setup_remote_server
    deploy_application
    setup_ssl_certificate
    setup_firewall
    start_services
    check_dns
    
    # 完了メッセージ
    echo ""
    echo -e "${GREEN}========================================"
    echo "デプロイ完了！"
    echo "========================================"
    echo ""
    echo "アクセスURL: https://your-domain.com"
    echo ""
    echo "管理者ログイン:"
    echo "  ユーザー名: admin"
    echo "  パスワード: secure-password-2024"
    echo ""
    echo "確認コマンド:"
    echo "  ssh $SSH_USER@$SERVER_IP 'cd /opt/webai && docker-compose -f docker-compose.prod.yml ps'"
    echo "  ssh $SSH_USER@$SERVER_IP 'cd /opt/webai && docker-compose -f docker-compose.prod.yml logs -f'"
    echo ""
    echo "モニタリング:"
    echo "  ssh $SSH_USER@$SERVER_IP 'cd /opt/webai && ./monitor.sh'"
    echo -e "${NC}"
}

# 実行
main