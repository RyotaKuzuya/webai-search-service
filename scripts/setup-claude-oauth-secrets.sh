#!/bin/bash

# Script to set up Claude Max OAuth tokens as GitHub secrets
# This script helps you configure the required secrets for Claude OAuth authentication

echo "=========================================="
echo "Claude Max OAuth GitHub Secrets Setup"
echo "=========================================="
echo ""
echo "This script will help you set up the required GitHub secrets for Claude Max OAuth authentication."
echo ""
echo "Prerequisites:"
echo "1. You must have the GitHub CLI (gh) installed and authenticated"
echo "2. You must have already obtained OAuth tokens from Claude Max"
echo "3. You must have write access to the repository"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: GitHub CLI is not authenticated."
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
if [ -z "$REPO" ]; then
    echo "Error: Not in a git repository or cannot determine repository."
    echo "Please run this script from within your repository."
    exit 1
fi

echo "Repository: $REPO"
echo ""

# Function to set a secret
set_secret() {
    local secret_name=$1
    local prompt_text=$2
    
    echo ""
    echo "$prompt_text"
    echo -n "Enter value for $secret_name: "
    read -s secret_value
    echo ""
    
    if [ -z "$secret_value" ]; then
        echo "Warning: Empty value provided for $secret_name"
        return 1
    fi
    
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO"
    if [ $? -eq 0 ]; then
        echo "✓ Successfully set $secret_name"
    else
        echo "✗ Failed to set $secret_name"
        return 1
    fi
}

echo "Setting up Claude OAuth secrets..."
echo "================================="

# Set CLAUDE_ACCESS_TOKEN
set_secret "CLAUDE_ACCESS_TOKEN" "Please enter your Claude access token (from Claude Max OAuth):"

# Set CLAUDE_REFRESH_TOKEN
set_secret "CLAUDE_REFRESH_TOKEN" "Please enter your Claude refresh token (from Claude Max OAuth):"

# Set CLAUDE_EXPIRES_AT
set_secret "CLAUDE_EXPIRES_AT" "Please enter the token expiration timestamp (Unix timestamp):"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "The following secrets have been configured:"
echo "- CLAUDE_ACCESS_TOKEN"
echo "- CLAUDE_REFRESH_TOKEN"
echo "- CLAUDE_EXPIRES_AT"
echo ""
echo "Next steps:"
echo "1. Fork the claude-code-action repository"
echo "2. Add OAuth support to your forked action"
echo "3. Update the workflow file to use your forked action"
echo "4. Test the workflow by creating an issue with @claude mention"
echo ""
echo "For more information, see:"
echo "https://docs.github.com/en/actions/security-guides/encrypted-secrets"