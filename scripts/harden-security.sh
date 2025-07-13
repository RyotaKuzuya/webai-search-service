#!/bin/bash

# Security Hardening Script for WebAI Production
# This script applies security best practices

set -e

echo "========================================"
echo "WebAI Security Hardening"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running with appropriate permissions
if [ "$EUID" -ne 0 ]; then 
   echo -e "${YELLOW}Warning: Some security settings require root privileges${NC}"
fi

# Function to secure file permissions
secure_permissions() {
    echo -e "${YELLOW}Setting secure file permissions...${NC}"
    
    # Secure sensitive files
    chmod 600 .env 2>/dev/null || true
    chmod 600 .env.sample 2>/dev/null || true
    chmod 700 claude-config/ 2>/dev/null || true
    chmod 700 certbot/conf/ 2>/dev/null || true
    
    # Secure scripts
    chmod 750 *.sh 2>/dev/null || true
    
    # Secure logs
    chmod 750 logs/ 2>/dev/null || true
    
    echo -e "${GREEN}✓ File permissions secured${NC}"
}

# Function to create security directory
create_security_dirs() {
    echo -e "${YELLOW}Creating security directories...${NC}"
    
    mkdir -p security
    mkdir -p logs/{nginx,webapp,certbot}
    
    echo -e "${GREEN}✓ Security directories created${NC}"
}

# Function to generate strong secrets
generate_secrets() {
    echo -e "${YELLOW}Checking secrets...${NC}"
    
    # Check if SECRET_KEY is still default
    if grep -q "your-secret-key-here-please-change-this" .env 2>/dev/null; then
        echo -e "${RED}✗ Default SECRET_KEY detected!${NC}"
        NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s/your-secret-key-here-please-change-this/$NEW_SECRET/" .env
        echo -e "${GREEN}✓ Generated new SECRET_KEY${NC}"
    fi
    
    # Check if ADMIN_PASSWORD is still default
    if grep -q "your-secure-password-here" .env 2>/dev/null; then
        echo -e "${RED}✗ Default ADMIN_PASSWORD detected!${NC}"
        echo "Please set a strong admin password in .env file"
    fi
}

# Function to configure firewall
configure_firewall() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}Configuring firewall...${NC}"
        
        # Install ufw if not present
        which ufw >/dev/null || apt-get install -y ufw
        
        # Default policies
        ufw default deny incoming
        ufw default allow outgoing
        
        # Allow SSH (adjust port if needed)
        ufw allow 22/tcp comment "SSH"
        
        # Allow HTTP and HTTPS
        ufw allow 80/tcp comment "HTTP"
        ufw allow 443/tcp comment "HTTPS"
        
        # Enable firewall
        ufw --force enable
        
        echo -e "${GREEN}✓ Firewall configured${NC}"
    else
        echo -e "${YELLOW}⚠ Skipping firewall configuration (requires root)${NC}"
    fi
}

# Function to install fail2ban
install_fail2ban() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}Installing fail2ban...${NC}"
        
        # Install fail2ban
        apt-get update
        apt-get install -y fail2ban
        
        # Copy WebAI filter
        cp security/fail2ban-webai.conf /etc/fail2ban/filter.d/webai.conf
        
        # Create jail configuration
        cat > /etc/fail2ban/jail.d/webai.conf << EOF
[webai]
enabled = true
port = http,https
filter = webai
logpath = $(pwd)/logs/nginx/access.log
maxretry = 5
findtime = 600
bantime = 3600
EOF
        
        # Restart fail2ban
        systemctl restart fail2ban
        
        echo -e "${GREEN}✓ Fail2ban configured${NC}"
    else
        echo -e "${YELLOW}⚠ Skipping fail2ban installation (requires root)${NC}"
    fi
}

# Function to check SSL configuration
check_ssl() {
    echo -e "${YELLOW}Checking SSL configuration...${NC}"
    
    if [ -f "certbot/conf/live/your-domain.com/fullchain.pem" ]; then
        # Check certificate expiry
        expiry_date=$(openssl x509 -enddate -noout -in certbot/conf/live/your-domain.com/fullchain.pem | cut -d= -f2)
        echo -e "${GREEN}✓ SSL certificate valid until: $expiry_date${NC}"
        
        # Check SSL configuration strength
        # You can add SSL Labs API check here
    else
        echo -e "${YELLOW}⚠ SSL certificate not found${NC}"
    fi
}

# Function to create security report
create_security_report() {
    echo -e "${YELLOW}Creating security report...${NC}"
    
    REPORT_FILE="security/security-report-$(date +%Y%m%d).txt"
    
    cat > "$REPORT_FILE" << EOF
WebAI Security Report
Generated: $(date)
=====================================

1. File Permissions:
$(ls -la .env 2>/dev/null || echo ".env not found")
$(ls -la claude-config/ 2>/dev/null || echo "claude-config not found")

2. Docker Security:
$(docker version 2>/dev/null || echo "Docker not running")

3. Open Ports:
$(ss -tuln 2>/dev/null | grep LISTEN || echo "Cannot check ports")

4. SSL Status:
$([ -f "certbot/conf/live/your-domain.com/fullchain.pem" ] && echo "Certificate installed" || echo "Certificate not found")

5. Firewall Status:
$(ufw status 2>/dev/null || echo "Firewall not configured")

6. Container Status:
$(docker-compose ps 2>/dev/null || echo "Containers not running")

7. Disk Usage:
$(df -h /)

8. Memory Usage:
$(free -h)

=====================================
Recommendations:
- Regularly update all software packages
- Monitor logs for suspicious activity
- Perform regular backups
- Test restore procedures
- Review and update passwords periodically
EOF
    
    echo -e "${GREEN}✓ Security report created: $REPORT_FILE${NC}"
}

# Main execution
echo "Starting security hardening..."
echo "-----------------------------"

create_security_dirs
secure_permissions
generate_secrets
configure_firewall
install_fail2ban
check_ssl
create_security_report

echo ""
echo "========================================"
echo -e "${GREEN}Security hardening completed!${NC}"
echo "========================================"
echo ""
echo "Additional recommendations:"
echo "1. Review the security report in security/"
echo "2. Set up log rotation if not already done"
echo "3. Configure automated backups"
echo "4. Set up monitoring alerts"
echo "5. Regularly update all components"
echo ""
echo "To start monitoring:"
echo "  ./monitor.sh --daemon"