#!/bin/bash

# Production Deployment Script for your-domain.com
# This script deploys WebAI to production with SSL

set -e

echo "========================================"
echo "WebAI Production Deployment"
echo "Domain: your-domain.com"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running with appropriate permissions
if [ "$EUID" -eq 0 ]; then 
   echo -e "${YELLOW}Running as root${NC}"
fi

# Function to check DNS
check_dns() {
    echo "Checking DNS configuration..."
    
    # Check if dig is available
    if command -v dig &> /dev/null; then
        IP=$(dig +short your-domain.com)
        if [ -n "$IP" ]; then
            echo -e "${GREEN}✓ your-domain.com resolves to: $IP${NC}"
        else
            echo -e "${RED}✗ your-domain.com DNS not configured${NC}"
            echo "Please ensure DNS A record points to this server"
            exit 1
        fi
    else
        echo -e "${YELLOW}Warning: 'dig' command not found, skipping DNS check${NC}"
    fi
}

# Function to setup SSL
setup_ssl() {
    echo ""
    echo "Setting up SSL certificates..."
    
    # Check if certificates already exist
    if [ -d "certbot/conf/live/your-domain.com" ]; then
        echo -e "${GREEN}SSL certificates already exist${NC}"
        read -p "Do you want to renew them? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose run --rm certbot renew --force-renewal
        fi
    else
        echo "Obtaining new SSL certificates..."
        
        # Create directories
        mkdir -p certbot/conf certbot/www
        
        # Start nginx temporarily for certificate validation
        docker-compose up -d nginx
        sleep 5
        
        # Get certificates
        docker-compose run --rm certbot certonly \
            --webroot \
            --webroot-path=/var/www/certbot \
            --email admin@your-domain.com \
            --agree-tos \
            --no-eff-email \
            -d your-domain.com \
            -d www.your-domain.com
        
        # Stop temporary nginx
        docker-compose down
    fi
}

# Main deployment steps
echo "1. Pre-deployment checks..."
echo "---------------------------"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not installed${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker installed${NC}"
fi

# Check .env file
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create .env from .env.sample"
    exit 1
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Set production environment
echo ""
echo "2. Setting production environment..."
echo "-----------------------------------"
sed -i 's/FLASK_ENV=development/FLASK_ENV=production/' .env
echo -e "${GREEN}✓ Environment set to production${NC}"

# Use production nginx config
echo ""
echo "3. Configuring Nginx for production..."
echo "--------------------------------------"
if [ -f "nginx/conf.d/webai-dev.conf" ]; then
    mv nginx/conf.d/webai-dev.conf nginx/conf.d/webai-dev.conf.bak
fi
echo -e "${GREEN}✓ Production Nginx config active${NC}"

# Check DNS
echo ""
echo "4. DNS Configuration..."
echo "----------------------"
check_dns

# Setup SSL
echo ""
echo "5. SSL Certificate Setup..."
echo "--------------------------"
setup_ssl

# OAuth setup check
echo ""
echo "6. OAuth Configuration..."
echo "------------------------"
if [ -f "claude-config/claude_config.json" ]; then
    echo -e "${GREEN}✓ OAuth configuration found${NC}"
else
    echo -e "${YELLOW}! OAuth not configured${NC}"
    echo "Run ./setup-oauth.sh for real OAuth authentication"
fi

# Deploy with production compose
echo ""
echo "7. Starting production services..."
echo "---------------------------------"
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo ""
echo "Waiting for services to start..."
sleep 10

# Check services
echo ""
echo "8. Service Status..."
echo "-------------------"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "========================================"
echo -e "${GREEN}Production deployment complete!${NC}"
echo "========================================"
echo ""
echo "Access your application at:"
echo -e "${GREEN}https://your-domain.com${NC}"
echo ""
echo "Admin credentials:"
echo "  Username: admin"
echo "  Password: (check your .env file)"
echo ""
echo "Useful commands:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo "  docker-compose -f docker-compose.prod.yml ps"
echo "  docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "SSL certificate will auto-renew via certbot container."