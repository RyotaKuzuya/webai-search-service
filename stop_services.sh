#!/bin/bash
# WebAI サービス停止スクリプト

echo "Stopping WebAI services..."

# Stop services
if pgrep -f "simple_app.py" > /dev/null; then
    echo "Stopping simple_app.py..."
    pkill -f "simple_app.py"
fi

if pgrep -f "simple_api.py" > /dev/null; then
    echo "Stopping simple_api.py..."
    pkill -f "simple_api.py"
fi

if pgrep -f "claude_simple_session_api.py" > /dev/null; then
    echo "Stopping claude_simple_session_api.py..."
    pkill -f "claude_simple_session_api.py"
fi

sleep 2

# Check if stopped
echo -e "\n=== Service Status ==="
if pgrep -f "simple_app.py|simple_api.py|claude_simple_session_api.py" > /dev/null; then
    echo "Some services are still running:"
    ps aux | grep -E "(simple_app|simple_api|claude_simple_session)" | grep -v grep
else
    echo "All services stopped successfully!"
fi