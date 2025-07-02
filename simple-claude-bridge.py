#!/usr/bin/env python3
"""
Simple Claude Bridge - Direct integration with Claude CLI
"""

import os
import json
import subprocess
import asyncio
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import tempfile

app = Flask(__name__)
CORS(app, origins=["*"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Claude binary path
CLAUDE_PATH = "/home/ubuntu/.npm-global/bin/claude"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    claude_exists = os.path.exists(CLAUDE_PATH)
    return jsonify({
        "status": "healthy",
        "service": "simple-claude-bridge",
        "claude_available": claude_exists
    })

@app.route('/message', methods=['POST'])
def message():
    """Simple message endpoint that calls claude CLI"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    logger.info(f"Received message: {content[:50]}...")
    
    def generate():
        try:
            # Create a temporary file with the message
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            # Use claude CLI in non-interactive mode
            cmd = [CLAUDE_PATH, "chat", "--once", f"< {temp_file}"]
            
            logger.info(f"Executing: {' '.join(cmd)}")
            
            # Execute via shell to handle input redirection
            process = subprocess.Popen(
                f"{CLAUDE_PATH} chat --once < {temp_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Stream output line by line
            output_lines = []
            for line in process.stdout:
                if line.strip():
                    output_lines.append(line.rstrip())
                    yield json.dumps({"content": line.rstrip()}) + "\n"
            
            # Wait for process to complete
            process.wait()
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            # If no output, provide a fallback response
            if not output_lines:
                logger.warning("No output from Claude, using fallback")
                fallback = "申し訳ございません。現在応答を生成できません。システムを確認してください。"
                yield json.dumps({"content": fallback}) + "\n"
            
            yield json.dumps({"status": "complete"}) + "\n"
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            yield json.dumps({"error": str(e)}) + "\n"
    
    return Response(generate(), mimetype='application/x-ndjson')

if __name__ == '__main__':
    port = 8001  # Different port to avoid conflicts
    logger.info(f"Starting Simple Claude Bridge on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)