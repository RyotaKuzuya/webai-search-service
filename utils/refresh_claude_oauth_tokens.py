#!/usr/bin/env python3
"""
Script to refresh Claude OAuth tokens and update GitHub secrets
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
import requests

def refresh_oauth_token(refresh_token, client_id=None, client_secret=None):
    """
    Refresh the OAuth access token using the refresh token
    
    Args:
        refresh_token: The refresh token
        client_id: OAuth client ID (if required)
        client_secret: OAuth client secret (if required)
    
    Returns:
        dict: New token information including access_token, refresh_token, and expires_at
    """
    # Claude OAuth endpoint (update with actual endpoint)
    token_url = "https://api.anthropic.com/oauth/token"
    
    # Prepare the request
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    # Add client credentials if provided
    if client_id and client_secret:
        data["client_id"] = client_id
        data["client_secret"] = client_secret
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Calculate expiration timestamp
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
        expires_at = int(time.time()) + expires_in
        
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", refresh_token),
            "expires_at": expires_at,
            "expires_in": expires_in
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def update_github_secret(secret_name, secret_value):
    """
    Update a GitHub secret using the gh CLI
    
    Args:
        secret_name: Name of the secret
        secret_value: Value of the secret
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use gh CLI to set the secret
        process = subprocess.Popen(
            ["gh", "secret", "set", secret_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=secret_value)
        
        if process.returncode == 0:
            print(f"✓ Successfully updated {secret_name}")
            return True
        else:
            print(f"✗ Failed to update {secret_name}: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {secret_name}: {e}")
        return False

def check_token_expiration(expires_at):
    """
    Check if token is expired or will expire soon
    
    Args:
        expires_at: Unix timestamp of token expiration
    
    Returns:
        tuple: (is_expired, time_until_expiry_seconds)
    """
    current_time = int(time.time())
    time_until_expiry = expires_at - current_time
    
    # Consider token expired if less than 5 minutes remaining
    is_expired = time_until_expiry < 300
    
    return is_expired, time_until_expiry

def main():
    """Main function to refresh Claude OAuth tokens"""
    
    print("Claude OAuth Token Refresh")
    print("==========================")
    print()
    
    # Get current tokens from environment or GitHub secrets
    refresh_token = os.environ.get("CLAUDE_REFRESH_TOKEN")
    expires_at = os.environ.get("CLAUDE_EXPIRES_AT")
    
    if not refresh_token:
        print("Error: CLAUDE_REFRESH_TOKEN not found in environment")
        print("Please set it as an environment variable or GitHub secret")
        return 1
    
    # Check if refresh is needed
    if expires_at:
        try:
            expires_at_int = int(expires_at)
            is_expired, time_remaining = check_token_expiration(expires_at_int)
            
            if not is_expired:
                hours_remaining = time_remaining / 3600
                print(f"Token is still valid for {hours_remaining:.1f} hours")
                
                # Optional: force refresh if requested
                if "--force" not in sys.argv:
                    print("Use --force to refresh anyway")
                    return 0
                else:
                    print("Forcing token refresh...")
                    
        except ValueError:
            print("Warning: Invalid CLAUDE_EXPIRES_AT value")
    
    # Get optional client credentials
    client_id = os.environ.get("CLAUDE_CLIENT_ID")
    client_secret = os.environ.get("CLAUDE_CLIENT_SECRET")
    
    print("Refreshing OAuth tokens...")
    
    # Refresh the token
    new_tokens = refresh_oauth_token(refresh_token, client_id, client_secret)
    
    if not new_tokens:
        print("Failed to refresh tokens")
        return 1
    
    print("✓ Successfully refreshed tokens")
    print(f"  New token expires at: {datetime.fromtimestamp(new_tokens['expires_at'])}")
    
    # Update GitHub secrets if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS"):
        print("\nUpdating GitHub secrets...")
        
        success = True
        success &= update_github_secret("CLAUDE_ACCESS_TOKEN", new_tokens["access_token"])
        success &= update_github_secret("CLAUDE_REFRESH_TOKEN", new_tokens["refresh_token"])
        success &= update_github_secret("CLAUDE_EXPIRES_AT", str(new_tokens["expires_at"]))
        
        if success:
            print("\n✓ All secrets updated successfully")
        else:
            print("\n✗ Some secrets failed to update")
            return 1
    else:
        # Output for local testing
        print("\nNew tokens (for local testing):")
        print(f"CLAUDE_ACCESS_TOKEN={new_tokens['access_token'][:20]}...")
        print(f"CLAUDE_REFRESH_TOKEN={new_tokens['refresh_token'][:20]}...")
        print(f"CLAUDE_EXPIRES_AT={new_tokens['expires_at']}")
        
        # Save to local file for testing
        with open(".claude_tokens.json", "w") as f:
            json.dump({
                "access_token": new_tokens["access_token"],
                "refresh_token": new_tokens["refresh_token"],
                "expires_at": new_tokens["expires_at"],
                "refreshed_at": int(time.time())
            }, f, indent=2)
        print("\nTokens saved to .claude_tokens.json (add to .gitignore!)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())