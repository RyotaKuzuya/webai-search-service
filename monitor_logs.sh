#!/bin/bash
echo "Monitoring logs..."
echo "==================="

# Start monitoring in background
docker logs -f webai-app 2>&1 | grep -E "Received message|stream_chunk|error|Error" &
APP_PID=$!

docker logs -f webai-claude-api 2>&1 | grep -E "Processing|Error|error" &
API_PID=$!

# Wait for user input
echo "Press Ctrl+C to stop monitoring"
wait

# Clean up
kill $APP_PID $API_PID 2>/dev/null