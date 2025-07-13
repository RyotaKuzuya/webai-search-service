#!/usr/bin/env python3
"""
Deploy to Replit.com - Free hosting with web IDE
This script prepares the project for Replit deployment
"""

import os
import json

def create_replit_config():
    """Create .replit configuration file"""
    config = {
        "run": "cd backend && python app.py",
        "language": "python3",
        "entrypoint": "backend/app.py",
        "hidden": [".config", "**/__pycache__", "**/.mypy_cache", "**/*.pyc"],
        "modules": ["python-3.10:v18-20230807-322e88b"]
    }
    
    with open(".replit", "w") as f:
        json.dump(config, f, indent=2)
    print("✓ Created .replit config")

def create_replit_nix():
    """Create replit.nix for system dependencies"""
    nix_content = """{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.python310Packages.poetry
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
      pkgs.xorg.libX11
    ];
    PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
    LANG = "en_US.UTF-8";
    STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
    PRYBAR_PYTHON_BIN = "${pkgs.replitPackages.prybar-python310}/bin/prybar-python310";
  };
}"""
    
    with open("replit.nix", "w") as f:
        f.write(nix_content)
    print("✓ Created replit.nix")

def create_pyproject():
    """Create pyproject.toml for Poetry"""
    pyproject = """[tool.poetry]
name = "webai"
version = "1.0.0"
description = "WebAI - AI Chat with Web Search"
authors = ["WebAI Team"]

[tool.poetry.dependencies]
python = "^3.10"
Flask = "^3.0.0"
Flask-SocketIO = "^5.3.5"
Flask-CORS = "^4.0.0"
python-socketio = "^5.10.0"
python-dotenv = "^1.0.0"
eventlet = "^0.33.3"
gunicorn = "^21.2.0"
requests = "^2.31.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""
    
    with open("pyproject.toml", "w") as f:
        f.write(pyproject)
    print("✓ Created pyproject.toml")

def create_main_py():
    """Create main.py for Replit"""
    main_content = '''#!/usr/bin/env python3
"""
Main entry point for Replit
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the app
from app import app, socketio

if __name__ == '__main__':
    # Replit provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    
    print("\\n" + "="*50)
    print("WebAI running on Replit")
    print("="*50)
    print(f"\\nYour app URL: https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co")
    print("\\nLogin credentials:")
    print("  Username: admin")
    print("  Password: Check .env file")
    print("="*50 + "\\n")
    
    # Run with socketio
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
'''
    
    with open("main.py", "w") as f:
        f.write(main_content)
    os.chmod("main.py", 0o755)
    print("✓ Created main.py")

def show_instructions():
    """Show deployment instructions"""
    print("\n" + "="*50)
    print("Replit Deployment Instructions")
    print("="*50 + "\n")
    
    print("Option 1: Import from GitHub")
    print("============================")
    print("1. Go to https://replit.com/new")
    print("2. Click 'Import from GitHub'")
    print("3. Paste your repository URL")
    print("4. Click 'Import from GitHub'")
    print("5. Replit will automatically set up everything")
    print()
    
    print("Option 2: Create New Repl")
    print("=========================")
    print("1. Go to https://replit.com/new/python")
    print("2. Name your repl 'webai'")
    print("3. Upload all project files")
    print("4. Click 'Run' button")
    print()
    
    print("Configuration:")
    print("=============")
    print("1. Click 'Secrets' (lock icon) in sidebar")
    print("2. Add these secrets:")
    print("   - SECRET_KEY: (generate a secure key)")
    print("   - ADMIN_PASSWORD: (set a secure password)")
    print()
    
    print("Features on Replit:")
    print("==================")
    print("✓ Automatic HTTPS")
    print("✓ Custom domain support")
    print("✓ Always-on (with Hacker plan)")
    print("✓ Environment variables")
    print("✓ Integrated database")
    print()
    
    print("Your app will be available at:")
    print("https://webai.YOUR-USERNAME.repl.co")
    print("\n" + "="*50)

def main():
    print("Preparing WebAI for Replit deployment...")
    
    # Create configuration files
    create_replit_config()
    create_replit_nix()
    create_pyproject()
    create_main_py()
    
    # Create .env if not exists
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""FLASK_ENV=production
SECRET_KEY=change-this-to-secure-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
CLAUDE_API_URL=http://localhost:8000""")
        print("✓ Created .env template")
    
    # Show instructions
    show_instructions()

if __name__ == "__main__":
    main()