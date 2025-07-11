#!/usr/bin/env python3
"""
Refresh Claude OAuth token
"""

import json
import requests
from datetime import datetime, timezone
import os

CONFIG_PATH = '/home/ubuntu/webai/claude-config/claude_config.json'

def refresh_token():
    """Refresh the Claude OAuth token"""
    
    # Read current config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(config['expires_at'].replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    
    print(f"Current token expires: {expires_at}")
    print(f"Current time: {now}")
    
    if expires_at > now:
        print(f"Token is still valid for {(expires_at - now).days} days")
    else:
        print("Token has expired!")
    
    # Attempt to refresh
    refresh_url = "https://api.anthropic.com/oauth/token"
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': config['refresh_token'],
        'client_id': config['client_id']
    }
    
    print("\nAttempting to refresh token...")
    
    try:
        response = requests.post(refresh_url, data=data)
        
        if response.status_code == 200:
            new_tokens = response.json()
            
            # Update config
            config['access_token'] = new_tokens['access_token']
            config['refresh_token'] = new_tokens['refresh_token']
            config['expires_at'] = new_tokens['expires_at']
            
            # Save updated config
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Token refreshed successfully!")
            print(f"New token expires: {new_tokens['expires_at']}")
            
            # Also save to GitHub format
            print("\n" + "="*80)
            print("GitHub Actions Token (CLAUDE_CODE_OAUTH_TOKEN):")
            print(new_tokens['access_token'])
            print("="*80)
            
        else:
            print(f"❌ Failed to refresh token: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")

if __name__ == "__main__":
    refresh_token()