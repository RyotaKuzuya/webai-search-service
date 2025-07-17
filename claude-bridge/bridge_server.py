#!/usr/bin/env python3
"""
Bridge server that runs on the host and executes claude commands
"""

import os
import json
import subprocess
import asyncio
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeExecutor:
    """Execute claude commands on the host system"""
    
    def __init__(self):
        self.claude_path = "/home/ubuntu/webai/claude-bridge/claude_wrapper.sh"
        self.check_claude()
    
    def check_claude(self):
        """Check if claude is available"""
        try:
            result = subprocess.run(
                [self.claude_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Claude available: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.error(f"Claude not found: {e}")
        return False
    
    def stream_claude_response(self, message, model="claude-opus-4-20250514"):
        """Stream response from claude"""
        try:
            # Create the command
            cmd = [self.claude_path, "chat", "--model", model]
            
            logger.info(f"Executing: {' '.join(cmd)}")
            logger.info(f"Message: {message[:100]}...")
            
            # Prepare environment
            env = os.environ.copy()
            env['NODE_PATH'] = '/home/ubuntu/.npm-global/lib/node_modules'
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                cwd='/home/ubuntu'
            )
            
            # Send the message
            process.stdin.write(message + "\n")
            process.stdin.flush()
            process.stdin.close()
            
            # Stream the output
            output_buffer = []
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Filter out prompts and empty lines
                line = line.rstrip()
                if line and not line.startswith("Human:") and not line.startswith("Assistant:"):
                    output_buffer.append(line)
                    yield json.dumps({
                        "content": line
                    }) + "\n"
            
            # Wait for process to complete
            process.wait(timeout=120)
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                logger.error(f"Claude error: {stderr}")
                yield json.dumps({
                    "error": f"Claude process failed: {stderr}"
                }) + "\n"
            else:
                yield json.dumps({
                    "status": "complete"
                }) + "\n"
                
        except subprocess.TimeoutExpired:
            process.kill()
            yield json.dumps({
                "error": "Request timed out after 120 seconds"
            }) + "\n"
        except Exception as e:
            logger.error(f"Error executing claude: {e}")
            yield json.dumps({
                "error": f"Failed to execute claude: {str(e)}"
            }) + "\n"

# Initialize executor
executor = ClaudeExecutor()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "claude-bridge",
        "timestamp": datetime.utcnow().isoformat(),
        "claude_available": executor.check_claude()
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that streams claude responses"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model = data.get('model', 'claude-opus-4-20250514')
        
        # Convert short model names to full names
        model_mapping = {
            'opus': 'claude-opus-4-20250514',
            'opus4': 'claude-opus-4-20250514',
            'sonnet': 'claude-3.5-sonnet-20240620',
            'haiku': 'claude-3.5-haiku-20241022'
        }
        model = model_mapping.get(model, model)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        logger.info(f"Received chat request: {message[:50]}...")
        
        def generate():
            yield from executor.stream_claude_response(message, model)
        
        return Response(
            generate(),
            mimetype='application/x-ndjson',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = 8585
    logger.info(f"Starting Claude Bridge Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)