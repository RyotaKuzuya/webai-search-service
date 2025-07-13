#!/usr/bin/env python3
"""
Simplified Claude Session API - Direct subprocess approach
"""

import os
import json
import subprocess
import uuid
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Claude CLI path
CLAUDE_CLI = "/home/ubuntu/.npm-global/bin/claude"

# Global session storage
sessions = {}
session_lock = threading.Lock()

class SimpleClaudeSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.conversation = []
        self.model = "sonnet"
        self.last_activity = time.time()
        self.creation_time = time.time()
        self.message_count = 0
        # Add system prompt for Japanese responses
        self.system_prompt = (
            "重要: あなたは別のPCで作業中のユーザーを支援しています。"
            "このサーバーのファイルやコマンドを操作しないでください。"
            "質問に対してWeb検索や知識に基づいた回答のみを提供してください。"
            "検索結果を使用した場合は、必ず情報源のURLを明記してください。"
            "すべての応答は日本語で行ってください。"
        )
        
    def send_message(self, message):
        """Send message to Claude and get response"""
        self.message_count += 1
        self.last_activity = time.time()
        
        # Store in conversation history
        self.conversation.append({"role": "user", "content": message})
        
        try:
            # Build full conversation for context
            full_prompt = self._build_prompt()
            
            # Determine timeout based on thinking mode
            if 'ultrathink' in message.lower():
                timeout = 1800  # 30 minutes
            elif 'megathink' in message.lower():
                timeout = 900   # 15 minutes
            else:
                timeout = 600   # 10 minutes minimum for all queries
            
            # Call Claude CLI directly with --print flag and model
            result = subprocess.run(
                [CLAUDE_CLI, "--print", "--model", self.model],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Claude error: {result.stderr}")
                error_msg = result.stderr.strip()
                if "job was not started" in error_msg and ("payments have failed" in error_msg or "spending limit" in error_msg):
                    raise Exception("Anthropicアカウントの支払いに問題があります。'Billing & plans'セクションで支払い情報を確認してください。")
                elif "max_tokens" in error_msg and "thinking.budget_tokens" in error_msg:
                    raise Exception("ultrathink (32K)モードは現在のCLI実装の制限により使用できません。代わりにmegathink (10K)またはthink harder (20K)をお使いください。")
                elif "rate limit" in error_msg.lower():
                    raise Exception("レート制限に達しました。しばらくお待ちください。")
                else:
                    # Also check stdout for error messages
                    if not error_msg and result.stdout:
                        stdout_lower = result.stdout.lower()
                        if "api error" in stdout_lower or "error" in stdout_lower:
                            error_msg = result.stdout.strip()
                    
                    # Handle empty or unhelpful error messages
                    if not error_msg or error_msg.strip() == "":
                        raise Exception("Claude APIからの応答でエラーが発生しました。しばらくしてからもう一度お試しください。")
                    else:
                        raise Exception(f"Claude CLI error: {error_msg[:200]}")
            
            response = result.stdout.strip()
            
            # Check if response contains API error even with returncode 0
            if response and "API Error:" in response:
                logger.error(f"API Error in response: {response}")
                if "max_tokens" in response and "thinking.budget_tokens" in response:
                    raise Exception("ultrathink (32K)モードは現在のCLI実装の制限により使用できません。代わりにmegathink (10K)またはthink harder (20K)をお使いください。")
                else:
                    raise Exception(f"APIエラーが発生しました: {response}")
            
            # Ensure response is not empty
            if not response:
                logger.warning("Empty response from Claude")
                response = "応答がありませんでした。もう一度お試しください。"
            
            # Store response in conversation
            self.conversation.append({"role": "assistant", "content": response})
            
            return response
            
        except subprocess.TimeoutExpired:
            raise Exception("Claude response timeout")
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            raise
    
    def _build_prompt(self):
        """Build conversation prompt"""
        if len(self.conversation) == 1:
            # First message, add system prompt
            return f"{self.system_prompt}\n\nユーザーの質問: {self.conversation[0]['content']}"
        
        # Build conversation context with system prompt
        prompt = self.system_prompt
        for i, msg in enumerate(self.conversation):
            if msg["role"] == "user":
                prompt += f"\n\nHuman: {msg['content']}"
            elif msg["role"] == "assistant":
                prompt += f"\n\nAssistant: {msg['content']}"
        
        # Add Human: for the current message if not already there
        if not prompt.endswith(self.conversation[-1]["content"]):
            prompt += f"\n\nHuman: {self.conversation[-1]['content']}"
            
        return prompt.strip()
    
    def clear_context(self):
        """Clear conversation history"""
        self.conversation = []
        self.last_activity = time.time()
    
    def set_model(self, model):
        """Set the model to use"""
        self.model = model
    
    def is_healthy(self):
        """Check if session is healthy"""
        return True  # Simple sessions are always healthy

def get_or_create_session(session_id=None):
    """Get existing session or create new one"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    with session_lock:
        if session_id not in sessions:
            session = SimpleClaudeSession(session_id)
            sessions[session_id] = session
            logger.info(f"Created session {session_id}")
        return sessions[session_id], session_id

def cleanup_old_sessions():
    """Clean up inactive sessions"""
    with session_lock:
        current_time = time.time()
        to_remove = []
        for sid, session in sessions.items():
            if current_time - session.last_activity > 1800:  # 30 minutes
                to_remove.append(sid)
                logger.info(f"Removing inactive session {sid}")
        for sid in to_remove:
            del sessions[sid]

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    with session_lock:
        active_sessions = len(sessions)
        session_details = []
        for sid, session in sessions.items():
            session_details.append({
                "id": sid,
                "healthy": True,
                "age": int(time.time() - session.creation_time),
                "last_activity": int(time.time() - session.last_activity),
                "message_count": session.message_count,
                "conversation_length": len(session.conversation)
            })
    
    return jsonify({
        "status": "healthy",
        "service": "claude-simple-session-api",
        "active_sessions": active_sessions,
        "sessions": session_details
    })

@app.route('/session/create', methods=['POST'])
def create_session():
    """Create new session"""
    try:
        session, session_id = get_or_create_session()
        return jsonify({"session_id": session_id, "status": "created"})
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/session/<session_id>/message', methods=['POST'])
def send_message(session_id):
    """Send message to session"""
    data = request.get_json()
    message = data.get('message', '')
    model = data.get('model', 'sonnet')
    
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
    
    try:
        session, _ = get_or_create_session(session_id)
        
        # Set model if different
        if model != session.model:
            session.set_model(model)
        
        # Send message and get response
        response = session.send_message(message)
        
        return jsonify({
            "session_id": session_id,
            "message": response
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/session/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    """Clear session context"""
    try:
        session, _ = get_or_create_session(session_id)
        session.clear_context()
        return jsonify({"status": "cleared", "session_id": session_id})
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/session/<session_id>/stop', methods=['POST'])
def stop_session(session_id):
    """Stop and remove session"""
    with session_lock:
        if session_id in sessions:
            del sessions[session_id]
            logger.info(f"Stopped session {session_id}")
            return jsonify({"status": "stopped"})
        else:
            return jsonify({"error": "Session not found"}), 404

# Periodic cleanup
def periodic_cleanup():
    while True:
        time.sleep(300)  # Every 5 minutes
        cleanup_old_sessions()

cleanup_thread = threading.Thread(target=periodic_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8003))
    logger.info(f"Starting Claude Simple Session API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)