#!/bin/bash

# WebAI Quick Start Script
# This script sets up and starts the WebAI application quickly

set -e

echo "========================================"
echo "WebAI Quick Start"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed.${NC}"
    echo "Please run: sudo ./install-docker.sh"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Docker daemon is not running.${NC}"
    echo "Please run: sudo systemctl start docker"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.sample .env
    # Set development mode
    sed -i 's/FLASK_ENV=production/FLASK_ENV=development/' .env
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Check if OAuth is configured
if [ ! -f claude-config/claude_config.json ]; then
    echo -e "${YELLOW}OAuth not configured. Setting up mock authentication...${NC}"
    ./setup-oauth.sh <<< "2"
    echo -e "${GREEN}✓ Mock authentication configured${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p claude-config claude-home certbot/conf certbot/www logs/nginx logs/webapp logs/certbot
echo -e "${GREEN}✓ Directories created${NC}"

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chmod 600 .env
chmod 700 claude-config/
echo -e "${GREEN}✓ Permissions set${NC}"

# Stop any running containers
echo -e "${YELLOW}Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Cleaned up${NC}"

# Build containers
echo -e "${YELLOW}Building containers (this may take a few minutes)...${NC}"
docker-compose build
echo -e "${GREEN}✓ Containers built${NC}"

# Start containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Containers started${NC}"

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo ""
echo "Checking service status..."
echo "--------------------------"

# Check webapp
WEBAPP_STATUS=$(docker-compose ps webapp 2>/dev/null | grep -c "Up" || echo "0")
if [ "$WEBAPP_STATUS" = "1" ]; then
    echo -e "${GREEN}✓ WebApp is running${NC}"
else
    echo -e "${RED}✗ WebApp is not running${NC}"
fi

# Check claude-api
API_STATUS=$(docker-compose ps claude-api 2>/dev/null | grep -c "Up" || echo "0")
if [ "$API_STATUS" = "1" ]; then
    echo -e "${GREEN}✓ Claude API is running${NC}"
else
    echo -e "${RED}✗ Claude API is not running${NC}"
fi

# Check nginx
NGINX_STATUS=$(docker-compose ps nginx 2>/dev/null | grep -c "Up" || echo "0")
if [ "$NGINX_STATUS" = "1" ]; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx is not running${NC}"
fi

echo ""
echo "========================================"
echo "WebAI is starting up!"
echo "========================================"
echo ""
echo "Access the application at:"
echo -e "${GREEN}http://localhost${NC}"
echo ""
echo "Login credentials:"
echo "  Username: admin"
echo "  Password: WebAI@2024SecurePass!"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f    # View logs"
echo "  docker-compose ps         # Check status"
echo "  docker-compose down       # Stop everything"
echo ""
echo -e "${YELLOW}NOTE: This is running in development mode with mock Claude responses.${NC}"
echo "For production use, complete the real OAuth authentication."