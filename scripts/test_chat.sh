#!/bin/bash
echo "Testing WebAI Chat API..."

# Test health endpoint
echo "1. Testing health endpoint:"
curl -s https://your-domain.com/api/health -k | jq .

# Test Claude API health
echo -e "\n2. Testing Claude API health from webapp:"
docker exec webai-app curl -s http://claude-api:8000/health | jq .

# Test direct message to Claude API
echo -e "\n3. Testing direct message to Claude API:"
docker exec webai-claude-api curl -s -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}' | head -2

# Check WebSocket logs
echo -e "\n4. Recent WebSocket connections:"
docker logs webai-app 2>&1 | grep "WebSocket" | tail -5

# Check for any message handling
echo -e "\n5. Check message handling:"
docker logs webai-app 2>&1 | grep -i "message" | tail -5