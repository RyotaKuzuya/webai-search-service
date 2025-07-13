#!/usr/bin/env python3
"""
Test single Opus4 ultrathink request
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_single_ultrathink():
    """Test a single ultrathink request"""
    message = "ultrathink: P=NP問題について、現在の研究状況を要約してください"
    
    print(f"🚀 Starting single ultrathink request at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Message: {message}")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                'message': message,
                'model': 'opus4'
            },
            timeout=1800  # 30 minutes
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('message', '')
            
            print(f"✓ Success in {duration:.1f}s")
            print(f"Response length: {len(response_text):,} characters")
            print(f"\nFirst 500 chars of response:")
            print(response_text[:500] + "...")
            
        else:
            print(f"✗ HTTP {response.status_code}")
            print(f"Duration: {duration:.1f}s")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {response.text}")
                
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"✗ Timeout after {duration:.1f}s")
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"✗ Error after {duration:.1f}s: {e}")

if __name__ == "__main__":
    test_single_ultrathink()