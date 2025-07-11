#!/usr/bin/env python3
"""
Generate GitHub Actions token from Claude OAuth credentials
"""

import json
import requests
import sys

def generate_github_token():
    """Generate a token for GitHub Actions from Claude OAuth credentials"""
    
    # Read the Claude config
    try:
        with open('/home/ubuntu/webai/claude-config/claude_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return None
    
    # The access_token from OAuth can be used directly
    access_token = config.get('access_token')
    
    if not access_token:
        print("No access token found in config")
        return None
    
    print("OAuth Token for GitHub Actions:")
    print("=" * 80)
    print(access_token)
    print("=" * 80)
    print("\nTo use this token:")
    print("1. Go to your GitHub repository Settings")
    print("2. Navigate to Secrets and variables > Actions")
    print("3. Add a new secret named: CLAUDE_CODE_OAUTH_TOKEN")
    print("4. Paste the token above as the value")
    
    return access_token

if __name__ == "__main__":
    generate_github_token()