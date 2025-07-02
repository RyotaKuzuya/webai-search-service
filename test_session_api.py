#!/usr/bin/env python3
"""Test script for Claude Session API"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8002"

def test_session_lifecycle():
    """Test creating, using, and monitoring a session"""
    print("Testing Claude Session API...")
    
    # 1. Create session
    print("\n1. Creating session...")
    resp = requests.post(f"{API_BASE}/session/create")
    if resp.status_code != 200:
        print(f"Failed to create session: {resp.text}")
        return
    
    session_data = resp.json()
    session_id = session_data['session_id']
    print(f"Created session: {session_id}")
    
    # 2. Check health
    print("\n2. Checking health...")
    resp = requests.get(f"{API_BASE}/health")
    health = resp.json()
    print(f"Active sessions: {health['active_sessions']}")
    print(f"Healthy sessions: {health['healthy_sessions']}")
    if health['sessions']:
        for s in health['sessions']:
            print(f"  - Session {s['id'][:8]}... healthy={s['healthy']}, age={s['age']}s, messages={s['message_count']}")
    
    # 3. Send test message
    print("\n3. Sending test message...")
    resp = requests.post(f"{API_BASE}/session/{session_id}/message", 
                        json={"message": "Hello! What is 2+2?"})
    
    if resp.status_code == 200:
        response = resp.json()
        print(f"Response: {response['message'][:100]}...")
    else:
        print(f"Failed to send message: {resp.text}")
    
    # 4. Check health again
    print("\n4. Checking health after message...")
    resp = requests.get(f"{API_BASE}/health")
    health = resp.json()
    if health['sessions']:
        for s in health['sessions']:
            print(f"  - Session {s['id'][:8]}... healthy={s['healthy']}, messages={s['message_count']}")
    
    # 5. Test clear
    print("\n5. Testing clear...")
    resp = requests.post(f"{API_BASE}/session/{session_id}/clear")
    print(f"Clear status: {resp.status_code}")
    
    # 6. Send another message
    print("\n6. Sending message after clear...")
    resp = requests.post(f"{API_BASE}/session/{session_id}/message", 
                        json={"message": "What did I just ask you?"})
    
    if resp.status_code == 200:
        response = resp.json()
        print(f"Response: {response['message'][:100]}...")
    else:
        print(f"Failed: {resp.text}")
    
    # 7. Stop session
    print("\n7. Stopping session...")
    resp = requests.post(f"{API_BASE}/session/{session_id}/stop")
    print(f"Stop status: {resp.status_code}")
    
    # 8. Final health check
    print("\n8. Final health check...")
    resp = requests.get(f"{API_BASE}/health")
    health = resp.json()
    print(f"Active sessions: {health['active_sessions']}")

if __name__ == "__main__":
    test_session_lifecycle()