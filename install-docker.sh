#!/bin/bash

# Docker Installation Script for Ubuntu
# This script installs Docker and Docker Compose on Ubuntu systems

set -e

echo "======================================"
echo "Docker & Docker Compose Installation"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if running with sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}Please run this script with sudo${NC}"
        echo "Usage: sudo ./install-docker.sh"
        exit 1
    fi
}

# Function to install Docker
install_docker() {
    echo -e "${YELLOW}Installing Docker...${NC}"
    
    # Update package index
    apt-get update
    
    # Install prerequisites
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index again
    apt-get update
    
    # Install Docker Engine
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Add current user to docker group
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker $SUDO_USER
        echo -e "${GREEN}Added $SUDO_USER to docker group${NC}"
    fi
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo -e "${GREEN}✓ Docker installed successfully${NC}"
}

# Function to install Docker Compose
install_docker_compose() {
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    
    # Get latest version
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
    
    # Download Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Make it executable
    chmod +x /usr/local/bin/docker-compose
    
    # Create symbolic link
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo -e "${GREEN}✓ Docker Compose installed successfully${NC}"
}

# Function to verify installation
verify_installation() {
    echo ""
    echo -e "${YELLOW}Verifying installation...${NC}"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        echo -e "${GREEN}✓ Docker: $DOCKER_VERSION${NC}"
    else
        echo -e "${RED}✗ Docker installation failed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        echo -e "${GREEN}✓ Docker Compose: $COMPOSE_VERSION${NC}"
    else
        echo -e "${RED}✗ Docker Compose installation failed${NC}"
        exit 1
    fi
    
    # Test Docker
    echo ""
    echo -e "${YELLOW}Testing Docker...${NC}"
    docker run --rm hello-world
}

# Main installation flow
main() {
    check_sudo
    
    echo "This script will install:"
    echo "- Docker CE (Community Edition)"
    echo "- Docker Compose"
    echo ""
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    install_docker
    install_docker_compose
    verify_installation
    
    echo ""
    echo -e "${GREEN}======================================"
    echo "Installation completed successfully!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Log out and log back in for group changes to take effect"
    echo "2. Or run: newgrp docker"
    echo "3. Then continue with: ./setup-oauth.sh"
    echo -e "${NC}"
}

# Run main function
main