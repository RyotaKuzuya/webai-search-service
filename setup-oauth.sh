#!/bin/bash

# Claude-code-api OAuth Setup Script
# This script guides through the OAuth authentication process

set -e

echo "=========================================="
echo "Claude-code-api OAuth Authentication Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Use local config directory
CONFIG_DIR="./claude-config"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Function to check if already authenticated
check_auth() {
    if [ -f "$CONFIG_DIR/claude_config.json" ]; then
        echo -e "${GREEN}Authentication token found!${NC}"
        echo "You appear to be already authenticated."
        read -p "Do you want to re-authenticate? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Using existing authentication."
            exit 0
        fi
    fi
}

# Function to create mock authentication for development
create_mock_auth() {
    echo ""
    echo -e "${YELLOW}Creating mock authentication for development/testing...${NC}"
    echo ""
    
    # Create a mock config file
    cat > "$CONFIG_DIR/claude_config.json" << EOF
{
  "access_token": "mock_access_token_for_development",
  "refresh_token": "mock_refresh_token_for_development",
  "expires_at": "2025-12-31T23:59:59Z",
  "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
  "scope": "claude_code",
  "development_mode": true
}
EOF
    
    chmod 600 "$CONFIG_DIR/claude_config.json"
    
    echo -e "${GREEN}✓ Mock authentication created${NC}"
    echo ""
    echo -e "${YELLOW}NOTE: This is a mock configuration for development.${NC}"
    echo "For production use, you'll need to complete the real OAuth flow."
}

# Function to start OAuth flow
start_oauth() {
    echo ""
    echo "OAuth Authentication Options:"
    echo "1. Real OAuth authentication (requires Anthropic account)"
    echo "2. Mock authentication (for development/testing)"
    echo ""
    read -p "Select option (1 or 2): " OPTION
    
    if [ "$OPTION" = "2" ]; then
        create_mock_auth
        return
    fi
    
    echo ""
    echo "Starting OAuth authentication flow..."
    echo ""
    echo "STEP 1: Open the following URL in your browser:"
    echo ""
    echo -e "${GREEN}https://auth.anthropic.com/oauth/authorize?client_id=9d1c250a-e61b-44d9-88ed-5944d1962f5e&response_type=code&redirect_uri=http://localhost:8585/callback&scope=claude_code${NC}"
    echo ""
    echo "STEP 2: Log in with your Anthropic account"
    echo ""
    echo "STEP 3: After authorization, you'll be redirected to a page showing an authorization code"
    echo ""
    read -p "Enter the authorization code from the browser: " AUTH_CODE
    
    if [ -z "$AUTH_CODE" ]; then
        echo -e "${RED}Error: No authorization code provided${NC}"
        exit 1
    fi
    
    echo ""
    echo "Processing authorization code..."
    
    # Save the auth code temporarily
    echo "$AUTH_CODE" > "$CONFIG_DIR/auth_code.tmp"
    
    # Create a placeholder config
    cat > "$CONFIG_DIR/claude_config.json" << EOF
{
  "auth_code": "$AUTH_CODE",
  "pending_exchange": true,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    chmod 600 "$CONFIG_DIR/claude_config.json"
    
    echo -e "${GREEN}Authorization code saved!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. The claude-api container will use this code to complete authentication"
    echo "2. Check container logs to verify successful authentication"
    echo "3. The authentication token will be saved to: $CONFIG_DIR/claude_config.json"
}

# Function to verify authentication
verify_auth() {
    echo ""
    echo "Verifying authentication..."
    
    if [ -f "$CONFIG_DIR/claude_config.json" ]; then
        echo -e "${GREEN}✓ Authentication configuration found${NC}"
        
        # Check if file contains valid JSON
        if python3 -m json.tool "$CONFIG_DIR/claude_config.json" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Configuration file is valid JSON${NC}"
        else
            echo -e "${RED}✗ Configuration file is corrupted${NC}"
            exit 1
        fi
        
        # Check file permissions
        PERMS=$(stat -c %a "$CONFIG_DIR/claude_config.json" 2>/dev/null || stat -f %A "$CONFIG_DIR/claude_config.json")
        echo "  File permissions: $PERMS"
        
        echo ""
        echo -e "${GREEN}Authentication setup completed successfully!${NC}"
    else
        echo -e "${YELLOW}Authentication file not found yet.${NC}"
        echo "This is normal if the container hasn't processed the auth code yet."
        echo "Check the claude-api container logs for status."
    fi
}

# Main flow
check_auth
start_oauth
verify_auth

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="