#!/usr/bin/env python3
"""
Simple local test server - No Docker required
Run WebAI locally for testing without complex setup
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_color(message, color=NC):
    print(f"{color}{message}{NC}")

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_color("Python 3.7+ is required", RED)
        return False
    print_color(f"✓ Python {version.major}.{version.minor} detected", GREEN)
    return True

def create_venv():
    """Create virtual environment if not exists"""
    venv_path = Path("venv_local")
    if not venv_path.exists():
        print_color("Creating virtual environment...", YELLOW)
        subprocess.run([sys.executable, "-m", "venv", "venv_local"])
    return venv_path

def install_requirements():
    """Install required packages"""
    print_color("Installing requirements...", YELLOW)
    pip_path = "venv_local/bin/pip" if os.name != 'nt' else "venv_local\\Scripts\\pip"
    
    # Create a minimal requirements file for local testing
    with open("requirements-local.txt", "w") as f:
        f.write("""Flask==3.0.0
Flask-SocketIO==5.3.5
Flask-CORS==4.0.0
python-socketio==5.10.0
python-dotenv==1.0.0
eventlet==0.33.3
requests==2.31.0""")
    
    subprocess.run([pip_path, "install", "-r", "requirements-local.txt"])

def setup_env():
    """Setup environment variables"""
    if not Path(".env").exists():
        print_color("Creating .env file...", YELLOW)
        with open(".env", "w") as f:
            f.write("""FLASK_ENV=development
SECRET_KEY=local-test-secret-key-12345
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
CLAUDE_API_URL=http://localhost:8000""")
        print_color("✓ Created .env with test credentials", GREEN)
        print_color("  Username: admin", BLUE)
        print_color("  Password: admin123", BLUE)

def create_simple_app():
    """Create a simplified app for local testing"""
    simple_app = '''#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, socketio

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("WebAI Local Test Server")
    print("="*50)
    print("\\nAccess the application at: http://localhost:5000")
    print("\\nLogin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\\nPress Ctrl+C to stop the server")
    print("="*50 + "\\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
'''
    
    with open("run_simple.py", "w") as f:
        f.write(simple_app)
    
    os.chmod("run_simple.py", 0o755)

def create_mock_claude_api():
    """Create a simple mock Claude API for testing"""
    mock_api = '''#!/usr/bin/env python3
from flask import Flask, jsonify, request, Response
import json
import time

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "mock-claude-api"})

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "claude_available": True,
        "development_mode": True
    })

@app.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    content = data.get('content', '')
    
    def generate():
        responses = [
            f"I received your message: {content[:50]}...\\n\\n",
            "This is a local test environment.\\n\\n",
            "The real Claude API would provide actual AI responses.\\n\\n",
            "Everything is working correctly!"
        ]
        
        for chunk in responses:
            time.sleep(0.3)
            yield json.dumps({"content": chunk}) + "\\n"
        
        yield json.dumps({"status": "complete"}) + "\\n"
    
    return Response(generate(), mimetype='application/x-ndjson')

if __name__ == '__main__':
    print("Mock Claude API running on http://localhost:8000")
    app.run(port=8000, debug=True)
'''
    
    with open("mock_claude_api.py", "w") as f:
        f.write(mock_api)
    
    os.chmod("mock_claude_api.py", 0o755)

def start_services():
    """Start both services"""
    print_color("\nStarting services...", YELLOW)
    
    # Start mock Claude API in background
    python_path = "venv_local/bin/python" if os.name != 'nt' else "venv_local\\Scripts\\python"
    
    print_color("Starting Mock Claude API...", YELLOW)
    api_process = subprocess.Popen([python_path, "mock_claude_api.py"])
    time.sleep(2)
    
    print_color("Starting WebAI Application...", YELLOW)
    print_color("\n" + "="*50, BLUE)
    print_color("WebAI is starting at: http://localhost:5000", GREEN)
    print_color("="*50 + "\n", BLUE)
    
    # Open browser
    time.sleep(2)
    webbrowser.open("http://localhost:5000")
    
    try:
        # Start main app
        subprocess.run([python_path, "run_simple.py"])
    except KeyboardInterrupt:
        print_color("\nShutting down...", YELLOW)
        api_process.terminate()

def main():
    print_color("="*50, BLUE)
    print_color("WebAI Local Quick Start", BLUE)
    print_color("="*50, BLUE)
    
    if not check_python():
        return
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Setup steps
    create_venv()
    install_requirements()
    setup_env()
    create_simple_app()
    create_mock_claude_api()
    
    # Ensure OAuth config exists
    os.makedirs("claude-config", exist_ok=True)
    with open("claude-config/claude_config.json", "w") as f:
        f.write('{"development_mode": true}')
    
    print_color("\n✓ Setup completed!", GREEN)
    
    # Start services
    start_services()

if __name__ == "__main__":
    main()