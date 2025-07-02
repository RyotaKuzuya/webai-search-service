#!/bin/bash

# WebAI Health Monitoring and Auto-Recovery Script
# This script monitors all services and automatically recovers failed ones

# Configuration
LOG_FILE="/var/log/webai-monitor.log"
CHECK_INTERVAL=60  # seconds
MAX_RETRIES=3
ALERT_EMAIL="${ALERT_EMAIL:-admin@your-domain.com}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check service health
check_service_health() {
    local service=$1
    local url=$2
    local expected_status=${3:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

# Function to restart service
restart_service() {
    local service=$1
    log_message "WARNING: Restarting $service..."
    
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml restart "$service"
    else
        docker-compose restart "$service"
    fi
    
    # Wait for service to start
    sleep 30
}

# Function to check Docker container status
check_container_status() {
    local container=$1
    local status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null)
    
    if [ "$status" = "running" ]; then
        return 0
    else
        return 1
    fi
}

# Function to monitor all services
monitor_services() {
    local all_healthy=true
    
    # Check Nginx
    if check_container_status "webai-nginx"; then
        if check_service_health "nginx" "http://localhost/health"; then
            log_message "✓ Nginx: Healthy"
        else
            log_message "✗ Nginx: Health check failed"
            restart_service "nginx"
            all_healthy=false
        fi
    else
        log_message "✗ Nginx: Container not running"
        restart_service "nginx"
        all_healthy=false
    fi
    
    # Check WebApp
    if check_container_status "webai-app"; then
        if check_service_health "webapp" "http://localhost/api/health"; then
            log_message "✓ WebApp: Healthy"
        else
            log_message "✗ WebApp: Health check failed"
            restart_service "webapp"
            all_healthy=false
        fi
    else
        log_message "✗ WebApp: Container not running"
        restart_service "webapp"
        all_healthy=false
    fi
    
    # Check Claude API
    if check_container_status "webai-claude-api"; then
        # Claude API is internal, check through webapp
        log_message "✓ Claude API: Container running"
    else
        log_message "✗ Claude API: Container not running"
        restart_service "claude-api"
        all_healthy=false
    fi
    
    # Check SSL certificate expiry
    if [ -f "certbot/conf/live/your-domain.com/fullchain.pem" ]; then
        expiry_date=$(openssl x509 -enddate -noout -in certbot/conf/live/your-domain.com/fullchain.pem | cut -d= -f2)
        expiry_epoch=$(date -d "$expiry_date" +%s)
        current_epoch=$(date +%s)
        days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))
        
        if [ $days_until_expiry -lt 30 ]; then
            log_message "WARNING: SSL certificate expires in $days_until_expiry days"
            # Trigger renewal
            docker-compose exec certbot certbot renew
        else
            log_message "✓ SSL Certificate: Valid for $days_until_expiry more days"
        fi
    fi
    
    # Check disk space
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -gt 80 ]; then
        log_message "WARNING: Disk usage is at ${disk_usage}%"
        all_healthy=false
    else
        log_message "✓ Disk Space: ${disk_usage}% used"
    fi
    
    # Check memory usage
    memory_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ $memory_usage -gt 80 ]; then
        log_message "WARNING: Memory usage is at ${memory_usage}%"
    else
        log_message "✓ Memory: ${memory_usage}% used"
    fi
    
    return $([ "$all_healthy" = true ])
}

# Function to send alert
send_alert() {
    local message=$1
    log_message "ALERT: $message"
    
    # You can implement email alerts here
    # echo "$message" | mail -s "WebAI Alert" "$ALERT_EMAIL"
}

# Main monitoring loop
main() {
    log_message "Starting WebAI health monitoring..."
    
    while true; do
        log_message "=== Health Check Start ==="
        
        if monitor_services; then
            log_message "=== All services healthy ==="
        else
            log_message "=== Issues detected and addressed ==="
        fi
        
        # Sleep before next check
        sleep $CHECK_INTERVAL
    done
}

# Create log file if it doesn't exist
touch "$LOG_FILE"

# Check if running as daemon
if [ "$1" = "--daemon" ]; then
    # Run in background
    nohup "$0" >> "$LOG_FILE" 2>&1 &
    echo "Monitor started in background with PID: $!"
    echo $! > /var/run/webai-monitor.pid
else
    # Run in foreground
    main
fi