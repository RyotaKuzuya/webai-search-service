#!/usr/bin/env python3
import requests
import json

# Test direct bridge connection
print("Testing bridge server...")
response = requests.get("http://localhost:8585/health")
print(f"Bridge health: {response.json()}")

# Test chat
print("\nTesting chat...")
response = requests.post(
    "http://localhost:8585/chat",
    json={
        "message": "Hello, this is a test. Please respond briefly.",
        "model": "claude-opus-4-20250514"
    },
    stream=True
)

print("Response:")
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if "content" in data:
            print(data["content"])
        elif "status" in data:
            print(f"[{data['status']}]")
        elif "error" in data:
            print(f"Error: {data['error']}")