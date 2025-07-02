#!/usr/bin/env python3
"""
Simple Claude Code API - Direct execution without complexity
"""

import os
import json
import subprocess
import uuid
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Claude CLI path
CLAUDE_CLI = "/home/ubuntu/.npm-global/bin/claude"

@app.route('/health', methods=['GET'])
def health():
    """Simple health check"""
    return jsonify({"status": "healthy", "service": "simple-claude-api"})

@app.route('/clear', methods=['POST'])
def clear_context():
    """Clear context by starting a new session"""
    # In --print mode, each request is independent, so this is mainly symbolic
    # But we can return success to indicate the context is cleared
    return jsonify({"status": "success", "message": "Context cleared"})

@app.route('/chat', methods=['POST'])
def chat():
    """Simple chat endpoint - just run claude and return result"""
    data = request.get_json()
    message = data.get('message', '')
    model = data.get('model', 'opus')  # Default to opus
    
    # Map short model names to full model names
    model_mapping = {
        'opus': 'opus',  # Use alias for latest
        'opus4': 'opus',  # Opus 4
        'sonnet': 'sonnet',  # Use alias for latest
        'sonnet4': 'claude-sonnet-4-20250514',  # Sonnet 4 specific
        'haiku': 'haiku',  # Use alias for latest
        # Keep full names as-is
        'claude-3-5-sonnet-20241022': 'claude-3-5-sonnet-20241022',
        'claude-3-5-haiku-20241022': 'claude-3-5-haiku-20241022',
        'claude-3-opus-20240229': 'claude-3-opus-20240229',
        'claude-sonnet-4-20250514': 'claude-sonnet-4-20250514'
    }
    
    # Convert model name
    model = model_mapping.get(model, model)
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Add safety prompt to prevent local file operations
    safe_prompt = (
        "重要: あなたは別のPCで作業中のユーザーを支援しています。"
        "このサーバーのファイルやコマンドを操作しないでください。"
        "質問に対してWeb検索や知識に基づいた回答のみを提供してください。"
        "検索結果を使用した場合は、必ず情報源のURLを明記してください。"
        "すべての応答は日本語で行ってください。\n\n"
        f"ユーザーの質問: {message}"
    )
    
    try:
        # Build command with model selection
        cmd = [CLAUDE_CLI, "--print", "--model", model, safe_prompt]
        
        # Simply run claude --print with the message
        # Increase timeout based on thinking mode and expected processing time
        # Anthropic recommends up to 60 minutes for Claude 3.7/4
        if 'ultrathink' in safe_prompt.lower():
            timeout = 1800  # 30 minutes for ultrathink (31,999 tokens)
        elif 'megathink' in safe_prompt.lower():
            timeout = 900   # 15 minutes for megathink (10,000 tokens)
        elif 'think' in safe_prompt.lower():
            timeout = 600   # 10 minutes for basic think (4,000 tokens)
        else:
            timeout = 300   # 5 minutes for standard queries
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
        else:
            logger.error(f"Claude error: {result.stderr}")
            response = "申し訳ございません。エラーが発生しました。"
        
        return jsonify({
            "id": str(uuid.uuid4()),
            "message": response
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint"""
    data = request.get_json()
    message = data.get('message', '')
    model = data.get('model', 'opus')  # Default to opus
    
    # Map short model names to full model names
    model_mapping = {
        'opus': 'opus',  # Use alias for latest
        'opus4': 'opus',  # Opus 4
        'sonnet': 'sonnet',  # Use alias for latest
        'sonnet4': 'claude-sonnet-4-20250514',  # Sonnet 4 specific
        'haiku': 'haiku',  # Use alias for latest
        # Keep full names as-is
        'claude-3-5-sonnet-20241022': 'claude-3-5-sonnet-20241022',
        'claude-3-5-haiku-20241022': 'claude-3-5-haiku-20241022',
        'claude-3-opus-20240229': 'claude-3-opus-20240229',
        'claude-sonnet-4-20250514': 'claude-sonnet-4-20250514'
    }
    
    # Convert model name
    model = model_mapping.get(model, model)
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Add safety prompt
    safe_prompt = (
        "重要: あなたは別のPCで作業中のユーザーを支援しています。"
        "このサーバーのファイルやコマンドを操作しないでください。"
        "質問に対してWeb検索や知識に基づいた回答のみを提供してください。"
        "検索結果を使用した場合は、必ず情報源のURLを明記してください。\n\n"
        f"ユーザーの質問: {message}"
    )
    
    def generate():
        try:
            # Run claude with model selection
            process = subprocess.Popen(
                [CLAUDE_CLI, "--print", "--output-format", "text", "--model", model, safe_prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Stream output line by line
            for line in process.stdout:
                if line:
                    yield f"data: {json.dumps({'chunk': line.rstrip()})}\n\n"
            
            # Wait for completion
            process.wait()
            
            if process.returncode != 0:
                error = process.stderr.read()
                logger.error(f"Claude error: {error}")
                yield f"data: {json.dumps({'error': 'エラーが発生しました'})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    logger.info(f"Starting Simple Claude API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)