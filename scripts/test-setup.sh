#!/bin/bash

# Test script to verify WebAI setup
# This script checks all components and provides diagnostics

set -e

echo "========================================"
echo "WebAI Setup Test & Diagnostics"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to check test result
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((TESTS_FAILED++))
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "1. Checking prerequisites..."
echo "----------------------------"

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    check_result 0 "Docker installed: $DOCKER_VERSION"
else
    check_result 1 "Docker not installed"
    echo "   Run: sudo ./install-docker.sh"
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version)
    check_result 0 "Docker Compose installed: $COMPOSE_VERSION"
else
    check_result 1 "Docker Compose not installed"
fi

# Check if Docker daemon is running
if docker info >/dev/null 2>&1; then
    check_result 0 "Docker daemon is running"
else
    check_result 1 "Docker daemon is not running"
    echo "   Run: sudo systemctl start docker"
fi

echo ""
echo "2. Checking environment configuration..."
echo "---------------------------------------"

# Check .env file
if [ -f .env ]; then
    check_result 0 ".env file exists"
    
    # Check required variables
    source .env
    
    if [ -n "$SECRET_KEY" ] && [ "$SECRET_KEY" != "your-secret-key-here-please-change-this" ]; then
        check_result 0 "SECRET_KEY is configured"
    else
        check_result 1 "SECRET_KEY not properly configured"
    fi
    
    if [ -n "$ADMIN_PASSWORD" ] && [ "$ADMIN_PASSWORD" != "your-secure-password-here" ]; then
        check_result 0 "ADMIN_PASSWORD is configured"
    else
        check_result 1 "ADMIN_PASSWORD not properly configured"
    fi
else
    check_result 1 ".env file not found"
    echo "   Run: cp .env.sample .env && nano .env"
fi

echo ""
echo "3. Checking directory structure..."
echo "---------------------------------"

# Check required directories
DIRS=("backend" "frontend" "nginx" "claude-api")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_result 0 "Directory $dir exists"
    else
        check_result 1 "Directory $dir missing"
    fi
done

# Check volume directories
VOLUME_DIRS=("claude-config" "claude-home" "certbot/conf" "logs")
for dir in "${VOLUME_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_result 0 "Volume directory $dir exists"
    else
        check_result 1 "Volume directory $dir missing"
        mkdir -p "$dir"
    fi
done

echo ""
echo "4. Checking file permissions..."
echo "-------------------------------"

# Check .env permissions
if [ -f .env ]; then
    PERMS=$(stat -c %a .env 2>/dev/null || stat -f %A .env)
    if [ "$PERMS" = "600" ]; then
        check_result 0 ".env has secure permissions (600)"
    else
        check_result 1 ".env permissions not secure (current: $PERMS)"
        echo "   Run: chmod 600 .env"
    fi
fi

echo ""
echo "5. Checking Docker containers..."
echo "--------------------------------"

# Check if containers are defined
if docker-compose config >/dev/null 2>&1; then
    check_result 0 "Docker Compose configuration is valid"
    
    # List services
    echo "   Services defined:"
    docker-compose config --services | sed 's/^/     - /'
else
    check_result 1 "Docker Compose configuration error"
fi

echo ""
echo "6. Testing container build..."
echo "-----------------------------"

# Try to build containers
echo -e "${YELLOW}Building containers (this may take a few minutes)...${NC}"
if docker-compose build --quiet 2>/dev/null; then
    check_result 0 "Container build successful"
else
    check_result 1 "Container build failed"
    echo "   Check docker-compose logs for details"
fi

echo ""
echo "7. Checking OAuth setup..."
echo "--------------------------"

# Check OAuth config
if [ -f claude-config/claude_config.json ]; then
    check_result 0 "OAuth configuration found"
else
    check_result 1 "OAuth not configured"
    echo "   Run: ./setup-oauth.sh"
fi

echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! You can now run:${NC}"
    echo "  docker-compose up"
    echo ""
    echo "Then access the application at:"
    echo "  http://localhost"
else
    echo -e "${YELLOW}Some tests failed. Please fix the issues above before proceeding.${NC}"
fi

echo ""
echo "Additional commands:"
echo "  docker-compose logs -f    # View logs"
echo "  docker-compose ps         # Check container status"
echo "  docker-compose down       # Stop containers"