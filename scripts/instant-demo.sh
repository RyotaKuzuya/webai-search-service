#!/bin/bash

# Instant Demo - Get WebAI running in seconds
# This script provides the fastest way to see WebAI in action

echo "========================================"
echo "WebAI Instant Demo"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run with Python
run_python_demo() {
    echo -e "${YELLOW}Starting Python-based demo...${NC}"
    
    # Check Python
    if command_exists python3; then
        echo -e "${GREEN}✓ Python3 found${NC}"
        python3 run-local-simple.py
    elif command_exists python; then
        echo -e "${GREEN}✓ Python found${NC}"
        python run-local-simple.py
    else
        echo -e "${RED}✗ Python not found${NC}"
        echo "Please install Python 3.7+ from https://python.org"
        exit 1
    fi
}

# Function to run with Node.js (alternative)
run_node_demo() {
    echo -e "${YELLOW}Starting Node.js-based demo...${NC}"
    
    # Create simple Node.js server
    cat > demo-server.js << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

const server = http.createServer((req, res) => {
    if (req.url === '/') {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end(`
            <html>
            <head>
                <title>WebAI Demo</title>
                <style>
                    body { font-family: Arial; padding: 20px; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .button { background: #667eea; color: white; padding: 10px 20px; 
                             text-decoration: none; border-radius: 5px; display: inline-block; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>WebAI Demo Server</h1>
                    <p>Welcome to WebAI - AI Chat with Web Search</p>
                    <h2>Quick Start Options:</h2>
                    <ol style="text-align: left;">
                        <li>Run locally: <code>python3 run-local-simple.py</code></li>
                        <li>Deploy to Replit: <code>./deploy-to-replit.py</code></li>
                        <li>Deploy to Render: <code>./deploy-to-render.sh</code></li>
                        <li>Deploy to Railway: <code>./deploy-to-railway.sh</code></li>
                    </ol>
                    <a href="https://github.com/yourusername/webai" class="button">View on GitHub</a>
                </div>
            </body>
            </html>
        `);
    }
});

server.listen(PORT, () => {
    console.log(\`Demo server running at http://localhost:\${PORT}\`);
});
EOF
    
    node demo-server.js
}

# Function to open browser
open_browser() {
    local url=$1
    if command_exists xdg-open; then
        xdg-open "$url"
    elif command_exists open; then
        open "$url"
    elif command_exists start; then
        start "$url"
    fi
}

# Main execution
echo "Checking available runtimes..."
echo ""

# Option 1: Try Python first (full app)
if command_exists python3 || command_exists python; then
    echo -e "${GREEN}Option 1: Full Python Demo${NC}"
    echo "This will run the complete WebAI application locally"
    echo ""
    read -p "Start Python demo? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_python_demo
        exit 0
    fi
fi

# Option 2: Try Node.js (simple demo)
if command_exists node; then
    echo ""
    echo -e "${GREEN}Option 2: Simple Node.js Demo${NC}"
    echo "This will show deployment options"
    echo ""
    read -p "Start Node.js demo? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_node_demo
        exit 0
    fi
fi

# Option 3: Show manual options
echo ""
echo -e "${BLUE}Manual Demo Options:${NC}"
echo ""
echo "1. Use GitHub Codespaces (instant cloud IDE):"
echo "   - Push code to GitHub"
echo "   - Click 'Code' > 'Codespaces' > 'Create codespace'"
echo ""
echo "2. Use Gitpod (instant cloud IDE):"
echo "   - Push code to GitHub"
echo "   - Visit: https://gitpod.io/#https://github.com/yourusername/webai"
echo ""
echo "3. Use Replit (instant hosting):"
echo "   - Visit: https://replit.com/new"
echo "   - Import from GitHub"
echo ""
echo "4. Use StackBlitz (instant Node.js):"
echo "   - Visit: https://stackblitz.com/fork/github/yourusername/webai"
echo ""
echo -e "${YELLOW}No runtime found. Please install either:${NC}"
echo "- Python 3.7+: https://python.org"
echo "- Node.js 14+: https://nodejs.org"
echo "- Docker: https://docker.com"