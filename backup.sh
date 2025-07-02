#!/bin/bash

# WebAI Backup Script
# Creates comprehensive backups of all critical data

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/home/ubuntu/backups/webai}"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="webai_backup_${TIMESTAMP}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "========================================"
echo "WebAI Backup Process"
echo "Timestamp: $TIMESTAMP"
echo "========================================"
echo ""

# Function to backup files
backup_files() {
    local source=$1
    local name=$2
    
    if [ -e "$source" ]; then
        echo -e "${YELLOW}Backing up $name...${NC}"
        tar -czf "$BACKUP_DIR/${BACKUP_NAME}_${name}.tar.gz" "$source" 2>/dev/null
        echo -e "${GREEN}✓ $name backed up${NC}"
    else
        echo -e "${YELLOW}⚠ $name not found, skipping${NC}"
    fi
}

# Function to backup Docker volumes
backup_docker_volume() {
    local volume=$1
    local name=$2
    
    echo -e "${YELLOW}Backing up Docker volume: $volume...${NC}"
    
    # Check if volume exists
    if docker volume inspect "$volume" >/dev/null 2>&1; then
        # Create temporary container to access volume
        docker run --rm \
            -v "$volume":/backup-source:ro \
            -v "$BACKUP_DIR":/backup-dest \
            alpine tar -czf "/backup-dest/${BACKUP_NAME}_${name}.tar.gz" -C / backup-source
        echo -e "${GREEN}✓ Docker volume $volume backed up${NC}"
    else
        echo -e "${YELLOW}⚠ Docker volume $volume not found${NC}"
    fi
}

# Function to backup database (if applicable)
backup_database() {
    # If you add a database in the future, implement backup here
    echo -e "${YELLOW}No database to backup${NC}"
}

# Stop services for consistent backup
echo "Stopping services for consistent backup..."
if [ -f "docker-compose.prod.yml" ]; then
    docker-compose -f docker-compose.prod.yml stop
else
    docker-compose stop
fi

echo ""
echo "Starting backup process..."
echo "-------------------------"

# Backup configuration files
backup_files ".env" "env"
backup_files "claude-config" "claude-config"
backup_files "certbot/conf" "ssl-certificates"

# Backup application code
backup_files "backend" "backend"
backup_files "frontend" "frontend"
backup_files "nginx" "nginx-config"
backup_files "claude-api" "claude-api"

# Backup Docker compose files
backup_files "docker-compose.yml" "docker-compose"
backup_files "docker-compose.prod.yml" "docker-compose-prod"
backup_files "Dockerfile" "dockerfile"

# Backup logs
backup_files "logs" "logs"

# Backup scripts
echo -e "${YELLOW}Backing up scripts...${NC}"
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_scripts.tar.gz" *.sh 2>/dev/null || true
echo -e "${GREEN}✓ Scripts backed up${NC}"

# Create backup metadata
echo -e "${YELLOW}Creating backup metadata...${NC}"
cat > "$BACKUP_DIR/${BACKUP_NAME}_metadata.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "hostname": "$(hostname)",
    "backup_dir": "$BACKUP_DIR",
    "components": [
        "env",
        "claude-config",
        "ssl-certificates",
        "backend",
        "frontend",
        "nginx-config",
        "claude-api",
        "docker-compose",
        "logs",
        "scripts"
    ],
    "docker_images": $(docker images --format '{{json .}}' | jq -s '.'),
    "system_info": {
        "os": "$(uname -a)",
        "disk_usage": "$(df -h /)",
        "memory": "$(free -h)"
    }
}
EOF
echo -e "${GREEN}✓ Metadata created${NC}"

# Create master backup archive
echo -e "${YELLOW}Creating master backup archive...${NC}"
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" ${BACKUP_NAME}_*.tar.gz ${BACKUP_NAME}_metadata.json
rm -f ${BACKUP_NAME}_*.tar.gz ${BACKUP_NAME}_metadata.json
echo -e "${GREEN}✓ Master archive created: ${BACKUP_NAME}.tar.gz${NC}"

# Restart services
echo ""
echo "Restarting services..."
if [ -f "../docker-compose.prod.yml" ]; then
    cd .. && docker-compose -f docker-compose.prod.yml start
else
    cd .. && docker-compose start
fi

# Clean old backups
echo ""
echo -e "${YELLOW}Cleaning old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "webai_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo -e "${GREEN}✓ Old backups cleaned${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)

echo ""
echo "========================================"
echo -e "${GREEN}Backup completed successfully!${NC}"
echo "========================================"
echo "Backup file: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "Size: $BACKUP_SIZE"
echo ""
echo "To restore from this backup, run:"
echo "  ./restore.sh $BACKUP_DIR/${BACKUP_NAME}.tar.gz"