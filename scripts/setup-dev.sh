#!/bin/bash

# Development Environment Setup Script
# This script configures the environment for local development without SSL

set -e

echo "========================================"
echo "Development Environment Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Switch to development nginx config
echo -e "${YELLOW}Switching to development Nginx configuration...${NC}"

# Check if production config exists and back it up
if [ -f "nginx/conf.d/webai.conf" ]; then
    mv nginx/conf.d/webai.conf nginx/conf.d/webai.conf.prod
    echo -e "${GREEN}✓ Backed up production config${NC}"
fi

# Use development config
if [ -f "nginx/conf.d/webai-dev.conf" ]; then
    cp nginx/conf.d/webai-dev.conf nginx/conf.d/webai.conf
    echo -e "${GREEN}✓ Development config activated${NC}"
fi

# Set development environment
echo -e "${YELLOW}Setting development environment...${NC}"
sed -i 's/FLASK_ENV=production/FLASK_ENV=development/' .env
echo -e "${GREEN}✓ Environment set to development${NC}"

# Create self-signed certificates for local development
echo -e "${YELLOW}Creating self-signed certificates...${NC}"
mkdir -p certbot/conf/live/localhost

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certbot/conf/live/localhost/privkey.pem \
    -out certbot/conf/live/localhost/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Development/CN=localhost"

cp certbot/conf/live/localhost/fullchain.pem certbot/conf/live/localhost/chain.pem

echo -e "${GREEN}✓ Self-signed certificates created${NC}"

echo ""
echo -e "${GREEN}========================================"
echo "Development setup completed!"
echo "========================================"
echo ""
echo "You can now run:"
echo "  docker-compose up"
echo ""
echo "Access the application at:"
echo "  http://localhost"
echo ""
echo "Note: Your browser will show a security warning"
echo "for the self-signed certificate. This is normal"
echo "for development.${NC}"