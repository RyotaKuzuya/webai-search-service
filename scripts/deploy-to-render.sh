#!/bin/bash

# Deploy to Render.com (Free hosting)
# Render provides free hosting with automatic HTTPS

echo "========================================"
echo "Deploy WebAI to Render.com (Free)"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create render.yaml for automatic deployment
create_render_config() {
    cat > render.yaml << EOF
services:
  # Web service
  - type: web
    name: webai-app
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 backend.app:app"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: ADMIN_USERNAME
        value: admin
      - key: ADMIN_PASSWORD
        generateValue: true
      - key: CLAUDE_API_URL
        value: http://localhost:8000
      - key: PYTHON_VERSION
        value: 3.11.0
EOF
    
    echo -e "${GREEN}✓ Created render.yaml${NC}"
}

# Create requirements.txt in root
create_requirements() {
    cp backend/requirements.txt requirements.txt
    echo -e "${GREEN}✓ Created root requirements.txt${NC}"
}

# Create Procfile for Heroku-style deployment
create_procfile() {
    cat > Procfile << EOF
web: cd backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:\$PORT app:app
EOF
    echo -e "${GREEN}✓ Created Procfile${NC}"
}

# Create start script
create_start_script() {
    cat > start.sh << 'EOF'
#!/bin/bash
cd backend
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
EOF
    chmod +x start.sh
    echo -e "${GREEN}✓ Created start.sh${NC}"
}

# Instructions
show_instructions() {
    echo ""
    echo -e "${YELLOW}Deployment Instructions:${NC}"
    echo ""
    echo "1. Create a Render account (free):"
    echo "   https://render.com/register"
    echo ""
    echo "2. Install Render CLI (optional):"
    echo "   npm install -g @render-oss/cli"
    echo ""
    echo "3. Deploy using Web UI:"
    echo "   a. Go to https://dashboard.render.com/new/web"
    echo "   b. Connect your GitHub/GitLab repository"
    echo "   c. Or use 'Public Git repository' with:"
    echo "      https://github.com/yourusername/webai"
    echo "   d. Click 'Create Web Service'"
    echo ""
    echo "4. Or deploy using CLI:"
    echo "   render create"
    echo "   render deploy"
    echo ""
    echo "5. Your app will be available at:"
    echo "   https://webai-app.onrender.com"
    echo ""
    echo -e "${YELLOW}Note: Free tier limitations:${NC}"
    echo "- Spins down after 15 minutes of inactivity"
    echo "- Limited to 750 hours/month"
    echo "- First request after spindown takes ~30 seconds"
}

# Main execution
echo "Preparing for Render deployment..."
create_render_config
create_requirements
create_procfile
create_start_script
show_instructions