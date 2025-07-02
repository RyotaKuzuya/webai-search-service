#!/usr/bin/env python3
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
            f"I received your message: {content[:50]}...\n\n",
            "This is a local test environment.\n\n",
            "The real Claude API would provide actual AI responses.\n\n",
            "Everything is working correctly!"
        ]
        
        for chunk in responses:
            time.sleep(0.3)
            yield json.dumps({"content": chunk}) + "\n"
        
        yield json.dumps({"status": "complete"}) + "\n"
    
    return Response(generate(), mimetype='application/x-ndjson')

if __name__ == '__main__':
    print("Mock Claude API running on http://localhost:8000")
    app.run(port=8000, debug=True)
