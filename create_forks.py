#!/usr/bin/env python3
"""
Create forks using GitHub API
"""

import requests
import os
import sys

def create_fork_via_api(owner, repo, token):
    """Create a fork using GitHub API"""
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Create fork
    fork_url = f'https://api.github.com/repos/{owner}/{repo}/forks'
    
    print(f"Creating fork of {owner}/{repo}...")
    
    response = requests.post(fork_url, headers=headers)
    
    if response.status_code == 202:
        print(f"✅ Successfully initiated fork of {owner}/{repo}")
        return True
    elif response.status_code == 401:
        print("❌ Authentication failed. Token may be invalid.")
        return False
    elif response.status_code == 404:
        print(f"❌ Repository {owner}/{repo} not found")
        return False
    else:
        print(f"❌ Failed to fork: {response.status_code}")
        print(response.json())
        return False

def main():
    # You need to provide a GitHub personal access token
    print("GitHub Fork Creator")
    print("==================")
    print("")
    print("This script requires a GitHub Personal Access Token (PAT)")
    print("To create one:")
    print("1. Go to https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it 'repo' scope")
    print("4. Copy the token")
    print("")
    
    token = input("Enter your GitHub Personal Access Token: ").strip()
    
    if not token:
        print("❌ No token provided")
        sys.exit(1)
    
    # Repositories to fork
    repos_to_fork = [
        ('anthropics', 'claude-code-action'),
        ('anthropics', 'claude-code-base-action')
    ]
    
    success_count = 0
    
    for owner, repo in repos_to_fork:
        if create_fork_via_api(owner, repo, token):
            success_count += 1
    
    print("")
    print(f"Forked {success_count}/{len(repos_to_fork)} repositories")
    
    if success_count == len(repos_to_fork):
        print("")
        print("✅ All repositories forked successfully!")
        print("Run ./setup-after-fork.sh to continue setup")

if __name__ == "__main__":
    main()