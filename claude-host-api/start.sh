#!/bin/bash
# Start Claude Host API

cd /home/ubuntu/webai/claude-host-api

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the server
echo "Starting Claude Host API on port 8000..."
nohup python3 claude_host_server.py > server.log 2>&1 &
echo $! > server.pid

# Wait for startup
sleep 3

# Check if running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Claude Host API started successfully!"
    echo "PID: $(cat server.pid)"
    echo "Logs: tail -f /home/ubuntu/webai/claude-host-api/server.log"
else
    echo "Failed to start Claude Host API"
    cat server.log
    exit 1
fi