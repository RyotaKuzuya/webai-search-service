#!/usr/bin/env python3
import requests
import json

# Test Claude API directly
try:
    print("Testing Claude API health endpoint...")
    response = requests.get("http://localhost:8001/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test message endpoint
try:
    print("\nTesting message endpoint...")
    response = requests.post(
        "http://localhost:8001/message",
        json={"content": "テスト"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    
    # Stream response
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            print(f"Stream: {data}")
except Exception as e:
    print(f"Error: {e}")