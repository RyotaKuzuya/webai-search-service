#!/bin/bash

# WebAI Complete Production Deployment Script
# This script handles the entire deployment process

set -e

echo "========================================"
echo "WebAI Complete Production Deployment"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}==== $1 ====${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    local prereqs_met=true
    
    # Check Docker
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓ Docker installed${NC}"
    else
        echo -e "${RED}✗ Docker not installed${NC}"
        echo "  Run: sudo ./install-docker.sh"
        prereqs_met=false
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✓ Docker Compose installed${NC}"
    else
        echo -e "${RED}✗ Docker Compose not installed${NC}"
        prereqs_met=false
    fi
    
    # Check .env file
    if [ -f ".env" ]; then
        echo -e "${GREEN}✓ .env file exists${NC}"
        
        # Check critical variables
        if grep -q "your-secret-key-here-please-change-this" .env; then
            echo -e "${YELLOW}  ⚠ Default SECRET_KEY detected${NC}"
            prereqs_met=false
        fi
        
        if grep -q "your-secure-password-here" .env; then
            echo -e "${YELLOW}  ⚠ Default ADMIN_PASSWORD detected${NC}"
            prereqs_met=false
        fi
    else
        echo -e "${RED}✗ .env file not found${NC}"
        echo "  Run: cp .env.sample .env && nano .env"
        prereqs_met=false
    fi
    
    # Check DNS
    echo -e "${YELLOW}Checking DNS configuration...${NC}"
    if command -v dig &> /dev/null; then
        if dig +short your-domain.com | grep -q .; then
            echo -e "${GREEN}✓ DNS configured for your-domain.com${NC}"
        else
            echo -e "${YELLOW}  ⚠ DNS may not be configured${NC}"
        fi
    fi
    
    if [ "$prereqs_met" = false ]; then
        echo ""
        echo -e "${RED}Prerequisites not met. Please fix the issues above.${NC}"
        exit 1
    fi
}

# Function to setup OAuth
setup_oauth() {
    print_section "OAuth Authentication Setup"
    
    if [ -f "claude-config/claude_config.json" ]; then
        echo -e "${GREEN}✓ OAuth already configured${NC}"
        read -p "Do you want to reconfigure? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    echo "Starting OAuth setup..."
    ./setup-oauth.sh
}

# Function to obtain SSL certificate
setup_ssl() {
    print_section "SSL Certificate Setup"
    
    if [ -d "certbot/conf/live/your-domain.com" ]; then
        echo -e "${GREEN}✓ SSL certificates already exist${NC}"
        return
    fi
    
    echo "Obtaining SSL certificate..."
    
    # Create required directories
    mkdir -p certbot/conf certbot/www
    
    # Start temporary nginx for validation
    docker-compose -f docker-compose.prod.yml up -d nginx
    sleep 5
    
    # Get certificate
    docker-compose run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email admin@your-domain.com \
        --agree-tos \
        --no-eff-email \
        -d your-domain.com \
        -d www.your-domain.com
    
    # Stop temporary nginx
    docker-compose -f docker-compose.prod.yml down
}

# Function to deploy application
deploy_application() {
    print_section "Deploying Application"
    
    # Build containers
    echo -e "${YELLOW}Building Docker containers...${NC}"
    docker-compose -f docker-compose.prod.yml build
    
    # Start services
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services
    echo -e "${YELLOW}Waiting for services to initialize...${NC}"
    sleep 15
    
    # Check status
    echo -e "${YELLOW}Checking service status...${NC}"
    docker-compose -f docker-compose.prod.yml ps
}

# Function to verify deployment
verify_deployment() {
    print_section "Verifying Deployment"
    
    local all_good=true
    
    # Check container status
    echo "Checking containers..."
    for service in nginx webapp claude-api; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "${service}.*Up"; then
            echo -e "${GREEN}✓ $service is running${NC}"
        else
            echo -e "${RED}✗ $service is not running${NC}"
            all_good=false
        fi
    done
    
    # Check HTTPS
    echo ""
    echo "Checking HTTPS..."
    if curl -s -o /dev/null -w "%{http_code}" https://your-domain.com | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ HTTPS is working${NC}"
    else
        echo -e "${YELLOW}⚠ HTTPS check failed (this may be normal if DNS is not propagated)${NC}"
    fi
    
    # Check API health
    echo ""
    echo "Checking API health..."
    if curl -s http://localhost/api/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ API is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ API health check failed${NC}"
    fi
    
    if [ "$all_good" = true ]; then
        echo ""
        echo -e "${GREEN}All checks passed!${NC}"
    else
        echo ""
        echo -e "${YELLOW}Some checks failed. Check logs for details:${NC}"
        echo "  docker-compose -f docker-compose.prod.yml logs"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    print_section "Setting Up Monitoring"
    
    read -p "Do you want to set up automated monitoring? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Start monitor daemon
        ./monitor.sh --daemon
        echo -e "${GREEN}✓ Monitoring daemon started${NC}"
        
        # Install systemd service if running as root
        if [ "$EUID" -eq 0 ]; then
            cp systemd/webai-monitor.service /etc/systemd/system/
            systemctl enable webai-monitor
            systemctl start webai-monitor
            echo -e "${GREEN}✓ Systemd service installed${NC}"
        fi
    fi
}

# Function to setup backups
setup_backups() {
    print_section "Setting Up Backups"
    
    read -p "Do you want to set up automated backups? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Test backup
        echo "Testing backup script..."
        ./backup.sh
        
        # Add to crontab
        echo "Adding to crontab..."
        (crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && ./backup.sh") | crontab -
        echo -e "${GREEN}✓ Daily backups scheduled at 2 AM${NC}"
    fi
}

# Function to apply security hardening
apply_security() {
    print_section "Security Hardening"
    
    # Basic security without root
    chmod 600 .env
    chmod 700 claude-config/
    echo -e "${GREEN}✓ File permissions secured${NC}"
    
    # Full hardening if root
    if [ "$EUID" -eq 0 ]; then
        read -p "Apply full security hardening? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./harden-security.sh
        fi
    else
        echo -e "${YELLOW}Run with sudo for full security hardening${NC}"
    fi
}

# Main deployment flow
main() {
    echo -e "${YELLOW}This script will deploy WebAI to production at your-domain.com${NC}"
    echo ""
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    setup_oauth
    setup_ssl
    apply_security
    deploy_application
    verify_deployment
    setup_monitoring
    setup_backups
    
    # Final summary
    print_section "Deployment Complete!"
    
    echo ""
    echo -e "${GREEN}WebAI has been deployed successfully!${NC}"
    echo ""
    echo "Access your application at:"
    echo -e "${BLUE}https://your-domain.com${NC}"
    echo ""
    echo "Admin login:"
    echo "  Username: admin"
    echo "  Password: (check your .env file)"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose -f docker-compose.prod.yml logs -f"
    echo "  Check status: docker-compose -f docker-compose.prod.yml ps"
    echo "  Restart:      docker-compose -f docker-compose.prod.yml restart"
    echo "  Monitor:      tail -f /var/log/webai-monitor.log"
    echo ""
    echo -e "${YELLOW}Remember to:${NC}"
    echo "  1. Save your .env file backup"
    echo "  2. Document your admin credentials"
    echo "  3. Monitor the service for the first 24 hours"
    echo "  4. Check PRODUCTION_CHECKLIST.md for post-deployment tasks"
}

# Run main function
main