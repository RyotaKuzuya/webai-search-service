#!/usr/bin/env python3
"""
Claude Host API Server
Runs on host system to provide direct access to claude CLI
"""

import os
import json
import subprocess
import asyncio
import uuid
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging

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
        "service": "claude-host-api",
        "claude_available": claude_exists,
        "claude_path": CLAUDE_PATH
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat endpoint"""
    data = request.get_json()
    messages = data.get('messages', [])
    model = data.get('model', 'claude-3-5-haiku-20241022')
    stream = data.get('stream', False)
    
    if not messages:
        return jsonify({"error": "No messages provided"}), 400
    
    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_message = msg.get('content', '')
            break
    
    if not user_message:
        return jsonify({"error": "No user message found"}), 400
    
    logger.info(f"Processing message: {user_message[:50]}...")
    
    if stream:
        return Response(stream_response(user_message, model), 
                       mimetype='text/event-stream')
    else:
        # Non-streaming response
        response = get_claude_response(user_message, model)
        return jsonify({
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(asyncio.get_event_loop().time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }]
        })

def stream_response(message, model):
    """Stream response using claude CLI"""
    try:
        # Prepare claude command
        cmd = [
            CLAUDE_PATH,
            "chat",
            "--model", model,
            "--no-tools",
            "--continue"
        ]
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Send the message
        process.stdin.write(message + "\n")
        process.stdin.flush()
        
        # Stream the output
        for line in process.stdout:
            if line.strip():
                # Format as SSE
                chunk = {
                    "id": f"chatcmpl-{uuid.uuid4()}",
                    "object": "chat.completion.chunk",
                    "created": int(asyncio.get_event_loop().time()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": line},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
        
        # Send finish message
        finish_chunk = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion.chunk",
            "created": int(asyncio.get_event_loop().time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(finish_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in stream_response: {e}")
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "server_error"
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"

def get_claude_response(message, model):
    """Get non-streaming response from claude"""
    try:
        cmd = [
            CLAUDE_PATH,
            "chat",
            "--model", model,
            "--no-tools",
            message
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.error(f"Claude error: {result.stderr}")
            return f"Error: {result.stderr}"
            
    except Exception as e:
        logger.error(f"Error calling claude: {e}")
        return f"Error: {str(e)}"

@app.route('/message', methods=['POST'])
def legacy_message():
    """Legacy message endpoint for compatibility"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    logger.info(f"Legacy message received: {content[:50]}...")
    
    def generate():
        try:
            # For now, use a simple echo command to test
            # We'll use claude API directly without the interactive mode
            cmd = [
                CLAUDE_PATH,
                "api",
                content
            ]
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env={**os.environ, 'TERM': 'dumb'}
            )
            
            # Stream output
            output_received = False
            for line in process.stdout:
                if line.strip():
                    output_received = True
                    logger.info(f"Claude output: {line.rstrip()}")
                    yield json.dumps({"content": line.rstrip()}) + "\n"
            
            # Check for errors
            stderr = process.stderr.read()
            if stderr:
                logger.error(f"Claude stderr: {stderr}")
            
            # If no output, send a default response
            if not output_received:
                logger.warning("No output from Claude, sending default response")
                yield json.dumps({"content": "申し訳ございません。現在応答を生成できません。"}) + "\n"
            
            yield json.dumps({"status": "complete"}) + "\n"
            
        except Exception as e:
            logger.error(f"Error in legacy_message: {e}", exc_info=True)
            yield json.dumps({"error": str(e)}) + "\n"
    
    return Response(generate(), mimetype='application/x-ndjson')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Claude Host API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)