#!/usr/bin/env python3
"""
Production-ready Claude API server
Provides HTTP endpoints for chat interactions with proper error handling
"""

import os
import json
import time
import uuid
import subprocess
import threading
import queue
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from simple_claude_bridge import SimpleClaudeBridge

app = Flask(__name__)
CORS(app, origins=["https://your-domain.com", "https://www.your-domain.com"])

# Production logging setup
if not os.path.exists('/app/logs'):
    os.makedirs('/app/logs')

# Configure logging with rotation
file_handler = RotatingFileHandler(
    '/app/logs/claude-api.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Configure app logger
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Claude API server starting up')

# Metrics tracking
metrics = {
    'requests_total': 0,
    'requests_success': 0,
    'requests_failed': 0,
    'average_response_time': 0,
    'start_time': datetime.utcnow().isoformat()
}

class ClaudeInterface:
    """Interface to Claude with production error handling"""
    
    def __init__(self):
        self.integration = SimpleClaudeBridge()
        self.is_configured = self._check_configuration()
        
    def _check_configuration(self):
        """Check if Claude is properly configured"""
        # Check if bridge is available
        if self.integration.check_bridge():
            app.logger.info("Claude bridge available")
            return True
        else:
            app.logger.warning("Claude bridge not available")
            return False
    
    def check_claude_binary(self):
        """Check if claude binary is available"""
        return self.integration.check_bridge()
    
    def process_message(self, message, model="claude-opus-4-20250514", web_search=True):
        """Process a message through Claude"""
        start_time = time.time()
        
        try:
            if not self.is_configured:
                yield json.dumps({
                    "error": "Claude is not configured. Please complete OAuth setup."
                }) + "\n"
                return
            
            # Use the real Claude integration
            app.logger.info(f"Processing message with model {model}, web_search={web_search}")
            yield from self.integration.send_message(message, model=model, web_search=web_search)
            
        except Exception as e:
            app.logger.error(f"Error processing message: {e}")
            yield json.dumps({
                "error": f"Internal server error: {str(e)}"
            }) + "\n"
        finally:
            # Update metrics
            response_time = time.time() - start_time
            metrics['average_response_time'] = (
                (metrics['average_response_time'] * metrics['requests_total'] + response_time) /
                (metrics['requests_total'] + 1)
            )
    
    # Removed _claude_response and _mock_response methods as they're now handled by ClaudeIntegration

# Initialize Claude interface
claude = ClaudeInterface()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "claude-api",
        "configured": claude.is_configured,
        "claude_available": claude.check_claude_binary(),
        "uptime_seconds": (datetime.utcnow() - datetime.fromisoformat(metrics['start_time'])).total_seconds()
    }
    
    # Determine overall health
    if not claude.is_configured:
        health_status["status"] = "degraded"
        health_status["message"] = "Claude not configured"
    
    return jsonify(health_status), 200 if health_status["status"] == "healthy" else 503

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get service metrics"""
    return jsonify(metrics)

@app.route('/status', methods=['GET'])
def status():
    """Get detailed API status"""
    return jsonify({
        "status": "running",
        "claude_configured": claude.is_configured,
        "claude_binary_available": claude.check_claude_binary(),
        "environment": "production",
        "metrics": metrics
    })

@app.route('/message', methods=['POST'])
def send_message():
    """Send a message to Claude and stream the response"""
    metrics['requests_total'] += 1
    
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            metrics['requests_failed'] += 1
            return jsonify({"error": "No content provided"}), 400
        
        app.logger.info(f"Processing message: {content[:50]}...")
        
        model = data.get('model', 'claude-opus-4-20250514')
        web_search = data.get('web_search', True)
        
        app.logger.info(f"Processing message with model={model}, web_search={web_search}")
        
        def generate():
            try:
                yield from claude.process_message(content, model=model, web_search=web_search)
                metrics['requests_success'] += 1
            except Exception as e:
                metrics['requests_failed'] += 1
                app.logger.error(f"Stream error: {e}")
                yield json.dumps({"error": str(e)}) + "\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='application/x-ndjson',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        metrics['requests_failed'] += 1
        app.logger.error(f"Request error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/setup', methods=['GET'])
def setup_info():
    """Get setup information"""
    return jsonify({
        "config_exists": os.path.exists(claude.config_path),
        "claude_configured": claude.is_configured,
        "oauth_url": "https://auth.anthropic.com/oauth/authorize?client_id=9d1c250a-e61b-44d9-88ed-5944d1962f5e&response_type=code&redirect_uri=http://localhost:8585/callback&scope=claude_code",
        "instructions": "Complete OAuth authentication for production use"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    
    # Production settings
    app.logger.info(f"Starting Claude API server on port {port} (Production)")
    
    # Note: In production, this is run by gunicorn, not directly
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )