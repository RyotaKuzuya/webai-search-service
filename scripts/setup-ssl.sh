#!/bin/bash

# SSL証明書取得スクリプト

echo "========================================"
echo "SSL証明書セットアップ"
echo "========================================"

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ドメインとメールの設定
DOMAIN="your-domain.com"
EMAIL="admin@your-domain.com"

echo -e "${YELLOW}ドメイン: $DOMAIN${NC}"
echo -e "${YELLOW}メール: $EMAIL${NC}"
echo ""

# Certbot用のディレクトリ作成
echo -e "${YELLOW}Certbot用ディレクトリを作成中...${NC}"
sudo mkdir -p /var/www/certbot
sudo chmod 755 /var/www/certbot

# 一時的なNginx設定（HTTP用）
echo -e "${YELLOW}一時的なNginx設定を作成中...${NC}"
sudo tee /etc/nginx/sites-available/webai-certbot > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Dockerコンテナを一時的に停止
echo -e "${YELLOW}Dockerコンテナを一時停止中...${NC}"
docker-compose -f docker-compose.http.yml down

# システムNginxを起動
echo -e "${YELLOW}システムNginxを起動中...${NC}"
sudo ln -sf /etc/nginx/sites-available/webai-certbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl start nginx
sudo nginx -t && sudo systemctl reload nginx

# SSL証明書取得
echo -e "${YELLOW}SSL証明書を取得中...${NC}"
sudo certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN

# 証明書の確認
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo -e "${GREEN}✓ SSL証明書取得成功！${NC}"
    
    # 証明書をプロジェクトディレクトリにコピー
    echo -e "${YELLOW}証明書をコピー中...${NC}"
    sudo mkdir -p ./certbot/conf
    sudo cp -RL /etc/letsencrypt/* ./certbot/conf/
    sudo chown -R $USER:$USER ./certbot
    
    # システムNginxを停止
    echo -e "${YELLOW}システムNginxを停止中...${NC}"
    sudo systemctl stop nginx
    
    # HTTPSバージョンのDocker Composeを起動
    echo -e "${YELLOW}HTTPS対応のDockerコンテナを起動中...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}✓ SSL設定完了！${NC}"
    echo ""
    echo "アクセスURL: https://$DOMAIN"
    echo ""
else
    echo -e "${RED}✗ SSL証明書の取得に失敗しました${NC}"
    echo "DNSが正しく設定されているか確認してください。"
    
    # システムNginxを停止してHTTPコンテナを再起動
    sudo systemctl stop nginx
    docker-compose -f docker-compose.http.yml up -d
fi