#!/bin/bash

# Deploy to Railway.app (Alternative free hosting)
# Railway provides easy deployment with automatic HTTPS

echo "========================================"
echo "Deploy WebAI to Railway.app"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create railway.json
create_railway_config() {
    cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    
    echo -e "${GREEN}✓ Created railway.json${NC}"
}

# Create nixpacks.toml for better control
create_nixpacks_config() {
    cat > nixpacks.toml << EOF
[phases.setup]
nixPkgs = ["python311", "gcc"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "cd backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:\$PORT app:app"
EOF
    
    echo -e "${GREEN}✓ Created nixpacks.toml${NC}"
}

# Create .env.example for Railway
create_env_example() {
    cat > .env.railway << EOF
FLASK_ENV=production
SECRET_KEY=generate-a-secure-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=generate-a-secure-password
CLAUDE_API_URL=http://localhost:8000
PORT=5000
EOF
    
    echo -e "${GREEN}✓ Created .env.railway${NC}"
}

# Instructions
show_instructions() {
    echo ""
    echo -e "${YELLOW}Railway Deployment Instructions:${NC}"
    echo ""
    echo "Option 1: Deploy via GitHub (Recommended)"
    echo "========================================="
    echo "1. Push your code to GitHub"
    echo "2. Go to https://railway.app/new"
    echo "3. Click 'Deploy from GitHub repo'"
    echo "4. Select your repository"
    echo "5. Railway will auto-deploy"
    echo ""
    echo "Option 2: Deploy via CLI"
    echo "========================"
    echo "1. Install Railway CLI:"
    echo "   npm install -g @railway/cli"
    echo ""
    echo "2. Login to Railway:"
    echo "   railway login"
    echo ""
    echo "3. Create new project:"
    echo "   railway init"
    echo ""
    echo "4. Deploy:"
    echo "   railway up"
    echo ""
    echo "5. Get your app URL:"
    echo "   railway open"
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo "Add these in Railway dashboard:"
    echo "- SECRET_KEY (generate secure key)"
    echo "- ADMIN_PASSWORD (set secure password)"
    echo ""
    echo -e "${GREEN}Your app will be available at:${NC}"
    echo "https://your-app.railway.app"
}

# Main execution
echo "Preparing for Railway deployment..."
create_railway_config
create_nixpacks_config
create_env_example
show_instructions