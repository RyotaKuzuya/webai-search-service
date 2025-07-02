#!/usr/bin/env python3
"""
Simple API server that provides a mock Claude interface for development
In production, this would wrap the actual claude-code CLI
"""

import os
import json
import time
import uuid
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're in development mode
DEV_MODE = True  # Default to development mode for now
try:
    config_path = '/root/.config/claude/claude_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            DEV_MODE = config.get('development_mode', True)
except Exception as e:
    logger.warning(f"Could not read config file: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "claude-api", "mode": "development" if DEV_MODE else "production"})

@app.route('/status', methods=['GET'])
def status():
    """Get API status"""
    return jsonify({
        "status": "running",
        "claude_available": True,
        "claude_version": "mock-1.0.0" if DEV_MODE else "claude-code-1.0.0",
        "development_mode": DEV_MODE
    })

@app.route('/message', methods=['POST'])
def send_message():
    """Send a message to Claude and stream the response"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    # Log the incoming message
    logger.info(f"Received message: {content[:50]}...")
    
    def generate():
        """Generate mock response stream"""
        if DEV_MODE:
            # Mock response for development
            if "テスト" in content or "test" in content.lower():
                responses = [
                    "テストメッセージを受信しました。",
                    "WebAIは正常に動作しています。",
                    "現在、開発モードで基本的な応答を返しています。"
                ]
            elif "こんにちは" in content or "hello" in content.lower():
                responses = [
                    "こんにちは！WebAIチャットサービスへようこそ。",
                    "どのようなことでお手伝いできますか？"
                ]
            else:
                responses = [
                    f"「{content[:30]}{'...' if len(content) > 30 else ''}」というメッセージを受信しました。",
                    "現在、基本的な応答モードで動作しています。",
                    "完全なClaude AI統合は準備中です。"
                ]
            
            for i, chunk in enumerate(responses):
                time.sleep(0.3)  # Simulate streaming delay
                yield json.dumps({"content": chunk}) + "\n"
            
            yield json.dumps({"status": "complete"}) + "\n"
        else:
            # In production, this would interface with actual claude-code
            yield json.dumps({"error": "Claude integration not implemented"}) + "\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/setup', methods=['GET'])
def setup_info():
    """Get setup information"""
    config_exists = os.path.exists('/root/.config/claude/claude_config.json')
    
    return jsonify({
        "config_exists": config_exists,
        "development_mode": DEV_MODE,
        "oauth_url": "https://auth.anthropic.com/oauth/authorize?client_id=9d1c250a-e61b-44d9-88ed-5944d1962f5e&response_type=code&redirect_uri=http://localhost:8585/callback&scope=claude_code",
        "instructions": "Use the setup-oauth.sh script to complete authentication"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    
    # Use production server if PRODUCTION env var is set
    if os.environ.get('PRODUCTION', '').lower() == 'true':
        # Import and run production server
        import api_server_production
        api_server_production.app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.info(f"Starting Claude API server on port {port} (Mode: {'Development' if DEV_MODE else 'Production'})")
        app.run(host='0.0.0.0', port=port, debug=False)