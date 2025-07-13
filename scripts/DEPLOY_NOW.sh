#!/bin/bash

# 本番環境を今すぐ動かすためのスクリプト
# このスクリプトは実際のサーバーで実行してください

echo "========================================"
echo "WebAI 本番環境 即座デプロイ"
echo "========================================"
echo ""

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 現在の環境をチェック
check_environment() {
    echo -e "${YELLOW}環境チェック中...${NC}"
    
    # OS確認
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo -e "${GREEN}✓ OS: $NAME $VERSION${NC}"
    fi
    
    # メモリ確認
    MEMORY=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
    echo -e "${GREEN}✓ メモリ: ${MEMORY}GB${NC}"
    
    # ディスク容量確認
    DISK=$(df -h / | awk 'NR==2{print $4}')
    echo -e "${GREEN}✓ 空き容量: ${DISK}${NC}"
    
    # IPアドレス確認
    IP=$(curl -s ifconfig.me || wget -qO- ifconfig.me)
    echo -e "${GREEN}✓ サーバーIP: ${IP}${NC}"
    echo ""
}

# 必要なソフトウェアをインストール
install_requirements() {
    echo -e "${YELLOW}必要なソフトウェアをインストール中...${NC}"
    
    # パッケージ更新
    sudo apt-get update -y
    
    # 基本ツール
    sudo apt-get install -y \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        certbot \
        python3-certbot-nginx \
        ufw
    
    # Docker インストール
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Dockerをインストール中...${NC}"
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi
    
    # Docker Compose インストール
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Docker Composeをインストール中...${NC}"
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    echo -e "${GREEN}✓ 必要なソフトウェアのインストール完了${NC}"
}

# ファイアウォール設定
setup_firewall() {
    echo -e "${YELLOW}ファイアウォールを設定中...${NC}"
    
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    echo "y" | sudo ufw enable
    
    echo -e "${GREEN}✓ ファイアウォール設定完了${NC}"
}

# アプリケーションのセットアップ
setup_application() {
    echo -e "${YELLOW}アプリケーションをセットアップ中...${NC}"
    
    # 環境変数設定
    if [ ! -f .env ]; then
        cp .env.sample .env
        
        # セキュアなキーを生成
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s/your-secret-key-here-please-change-this/$SECRET_KEY/" .env
        
        # パスワード設定
        echo -e "${YELLOW}管理者パスワードを設定してください:${NC}"
        read -s -p "パスワード: " ADMIN_PASS
        echo
        sed -i "s/your-secure-password-here/$ADMIN_PASS/" .env
    fi
    
    # 必要なディレクトリ作成
    mkdir -p claude-config certbot/conf certbot/www logs
    
    # OAuth設定（モック）
    echo '{"development_mode": true}' > claude-config/claude_config.json
    chmod 600 claude-config/claude_config.json
    
    echo -e "${GREEN}✓ アプリケーションセットアップ完了${NC}"
}

# SSL証明書の取得
setup_ssl() {
    echo -e "${YELLOW}SSL証明書を設定中...${NC}"
    
    read -p "ドメイン名を入力 (例: your-domain.com): " DOMAIN
    read -p "メールアドレスを入力: " EMAIL
    
    # ドメインを.envに保存
    sed -i "s/DOMAIN_NAME=.*/DOMAIN_NAME=$DOMAIN/" .env
    sed -i "s/LETSENCRYPT_EMAIL=.*/LETSENCRYPT_EMAIL=$EMAIL/" .env
    
    # 一時的なNginx設定
    sudo tee /etc/nginx/sites-available/webai-temp > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/webai-temp /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl restart nginx
    
    # SSL証明書取得
    sudo certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    echo -e "${GREEN}✓ SSL証明書取得完了${NC}"
}

# Dockerコンテナを起動
start_services() {
    echo -e "${YELLOW}サービスを起動中...${NC}"
    
    # Docker権限の確認
    if ! docker ps >/dev/null 2>&1; then
        echo -e "${YELLOW}Docker権限を更新中...${NC}"
        newgrp docker
    fi
    
    # コンテナビルドと起動
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    
    # 状態確認
    sleep 10
    docker-compose -f docker-compose.prod.yml ps
    
    echo -e "${GREEN}✓ サービス起動完了${NC}"
}

# メイン処理
main() {
    echo -e "${BLUE}このスクリプトは本番サーバーで実行してください${NC}"
    echo ""
    
    # 環境チェック
    check_environment
    
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    
    # セットアップ実行
    install_requirements
    setup_firewall
    setup_application
    setup_ssl
    start_services
    
    # 完了メッセージ
    echo ""
    echo -e "${GREEN}========================================"
    echo "デプロイ完了！"
    echo "========================================"
    echo ""
    echo "アクセスURL: https://$DOMAIN"
    echo ""
    echo "管理者ログイン:"
    echo "  ユーザー名: admin"
    echo "  パスワード: .envファイルを確認"
    echo ""
    echo "確認コマンド:"
    echo "  docker-compose -f docker-compose.prod.yml ps"
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
    echo -e "${NC}"
}

# スクリプト実行
main