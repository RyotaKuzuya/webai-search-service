#!/bin/bash
# WebAI サービス起動スクリプト

echo "Starting WebAI services..."

# Check if services are already running
if pgrep -f "simple_app.py" > /dev/null; then
    echo "simple_app.py is already running"
else
    echo "Starting simple_app.py..."
    nohup python3 simple_app.py > simple_app.log 2>&1 &
fi

if pgrep -f "simple_api.py" > /dev/null; then
    echo "simple_api.py is already running"
else
    echo "Starting simple_api.py..."
    nohup python3 simple_api.py > simple_api.log 2>&1 &
fi

if pgrep -f "claude_simple_session_api.py" > /dev/null; then
    echo "claude_simple_session_api.py is already running"
else
    echo "Starting claude_simple_session_api.py..."
    nohup python3 claude_simple_session_api.py > claude_simple_session_api.log 2>&1 &
fi

sleep 2

# Show status
echo -e "\n=== Service Status ==="
ps aux | grep -E "(simple_app|simple_api|claude_simple_session)" | grep -v grep

echo -e "\n=== Listening Ports ==="
ss -tuln | grep -E "(5000|8001|8003)"

echo -e "\nAll services started successfully!"
echo "Access the web interface at: http://localhost:5000"