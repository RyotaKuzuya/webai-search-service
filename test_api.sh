#!/bin/bash

# Test script for WebAI API endpoints

echo "Testing WebAI API Endpoints..."
echo "=============================="

# Test Simple API Health
echo -e "\n1. Testing Simple API Health:"
curl -s https://your-domain.com/api/simple/health | jq .

# Test Session API Health
echo -e "\n2. Testing Session API Health:"
curl -s https://your-domain.com/api/session/health | jq .

# Test Simple Chat
echo -e "\n3. Testing Simple Chat API:"
response=$(curl -X POST https://your-domain.com/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?"}' \
  -s)
echo "$response" | jq .

# Extract just the message
echo -e "\n4. Claude's response:"
echo "$response" | jq -r '.message'

echo -e "\n=============================="
echo "All tests completed!"