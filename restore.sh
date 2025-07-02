#!/bin/bash

# WebAI Restore Script
# Restores from a backup created by backup.sh

set -e

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    echo "Example: $0 /home/ubuntu/backups/webai/webai_backup_20240101_120000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/webai_restore_$$"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo "========================================"
echo "WebAI Restore Process"
echo "Backup file: $BACKUP_FILE"
echo "========================================"
echo ""

# Warning
echo -e "${RED}WARNING: This will restore all configurations and data.${NC}"
echo -e "${RED}Current data will be overwritten!${NC}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Create restore directory
mkdir -p "$RESTORE_DIR"

# Extract master archive
echo -e "${YELLOW}Extracting backup archive...${NC}"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"
echo -e "${GREEN}✓ Archive extracted${NC}"

# Stop services
echo ""
echo "Stopping services..."
if [ -f "docker-compose.prod.yml" ]; then
    docker-compose -f docker-compose.prod.yml down
else
    docker-compose down
fi

# Function to restore files
restore_files() {
    local archive_name=$1
    local destination=$2
    
    ARCHIVE_PATH=$(find "$RESTORE_DIR" -name "*_${archive_name}.tar.gz" | head -1)
    
    if [ -f "$ARCHIVE_PATH" ]; then
        echo -e "${YELLOW}Restoring $archive_name...${NC}"
        
        # Create parent directory if needed
        mkdir -p "$(dirname "$destination")"
        
        # Remove existing
        rm -rf "$destination"
        
        # Extract
        tar -xzf "$ARCHIVE_PATH" -C /
        echo -e "${GREEN}✓ $archive_name restored${NC}"
    else
        echo -e "${YELLOW}⚠ $archive_name backup not found${NC}"
    fi
}

echo ""
echo "Restoring components..."
echo "----------------------"

# Restore configuration files
restore_files "env" ".env"
restore_files "claude-config" "claude-config"
restore_files "ssl-certificates" "certbot/conf"

# Restore application code
restore_files "backend" "backend"
restore_files "frontend" "frontend"
restore_files "nginx-config" "nginx"
restore_files "claude-api" "claude-api"

# Restore Docker compose files
restore_files "docker-compose" "docker-compose.yml"
restore_files "docker-compose-prod" "docker-compose.prod.yml"
restore_files "dockerfile" "Dockerfile"

# Restore scripts
SCRIPTS_ARCHIVE=$(find "$RESTORE_DIR" -name "*_scripts.tar.gz" | head -1)
if [ -f "$SCRIPTS_ARCHIVE" ]; then
    echo -e "${YELLOW}Restoring scripts...${NC}"
    tar -xzf "$SCRIPTS_ARCHIVE"
    chmod +x *.sh
    echo -e "${GREEN}✓ Scripts restored${NC}"
fi

# Set correct permissions
echo ""
echo -e "${YELLOW}Setting permissions...${NC}"
chmod 600 .env 2>/dev/null || true
chmod 700 claude-config/ 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
echo -e "${GREEN}✓ Permissions set${NC}"

# Clean up
rm -rf "$RESTORE_DIR"

# Rebuild and start services
echo ""
echo "Rebuilding and starting services..."
docker-compose build
if [ -f "docker-compose.prod.yml" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

# Wait for services
echo ""
echo "Waiting for services to start..."
sleep 10

# Check services
echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "========================================"
echo -e "${GREEN}Restore completed successfully!${NC}"
echo "========================================"
echo ""
echo "Please verify:"
echo "1. All services are running: docker-compose ps"
echo "2. Application is accessible"
echo "3. SSL certificates are valid"
echo "4. OAuth authentication is working"
echo ""
echo "If there are issues, check logs:"
echo "  docker-compose logs -f"