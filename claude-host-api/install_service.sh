#!/bin/bash
# Install Claude Host API as systemd service

SERVICE_FILE="/etc/systemd/system/claude-host-api.service"

cat > claude-host-api.service << EOF
[Unit]
Description=Claude Host API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/webai/claude-host-api
Environment="PATH=/usr/bin:/bin:/home/ubuntu/.npm-global/bin"
Environment="HOME=/home/ubuntu"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/python3 /home/ubuntu/webai/claude-host-api/claude_host_api_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Installing Claude Host API service..."
sudo cp claude-host-api.service $SERVICE_FILE
sudo systemctl daemon-reload
sudo systemctl enable claude-host-api
sudo systemctl stop claude-host-api 2>/dev/null || true

# Kill any existing processes
ps aux | grep claude_host_api | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true

sudo systemctl start claude-host-api
sudo systemctl status claude-host-api

echo "Claude Host API service installed and started!"
echo "Check logs with: sudo journalctl -u claude-host-api -f"