#!/usr/bin/env python3
"""
Simple Claude Code API - Direct execution without complexity
"""

import os
import json
import subprocess
import uuid
import shlex
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
        'sonnet4': 'claude-sonnet-4-20250514',  # Sonnet 4 specific
        # Keep full names as-is
        'claude-sonnet-4-20250514': 'claude-sonnet-4-20250514'
    }
    
    # Convert model name
    model = model_mapping.get(model, model)
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Escape problematic patterns that can cause CLI parsing issues
    # Replace unclosed quotes and parentheses to prevent syntax errors
    escaped_message = message
    # Count quotes and add closing quote if odd number
    if escaped_message.count("'") % 2 == 1:
        escaped_message += "'"
    if escaped_message.count('"') % 2 == 1:
        escaped_message += '"'
    # Balance parentheses
    open_parens = escaped_message.count('(')
    close_parens = escaped_message.count(')')
    if open_parens > close_parens:
        escaped_message += ')' * (open_parens - close_parens)
    
    # Add safety prompt to prevent local file operations
    safe_prompt = (
        "重要: あなたは別のPCで作業中のユーザーを支援しています。"
        "このサーバーのファイルやコマンドを操作しないでください。"
        "質問に対してWeb検索や知識に基づいた回答のみを提供してください。"
        "検索結果を使用した場合は、必ず情報源のURLを明記してください。"
        "すべての応答は日本語で行ってください。\n\n"
        f"ユーザーの質問: {escaped_message}"
    )
    
    try:
        # Build command with model selection
        cmd = [CLAUDE_CLI, "--print", "--model", model]
        
        # Simply run claude --print with the message
        # Increase timeout based on thinking mode and expected processing time
        # Anthropic recommends up to 60 minutes for Claude 3.7/4
        if 'ultrathink' in safe_prompt.lower():
            timeout = 1800  # 30 minutes for ultrathink (31,999 tokens)
        elif 'megathink' in safe_prompt.lower():
            timeout = 900   # 15 minutes for megathink (10,000 tokens)
        else:
            timeout = 600   # 10 minutes minimum for all queries
        
        # Use stdin to pass the prompt to avoid shell escaping issues
        result = subprocess.run(
            cmd,
            input=safe_prompt,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            # Check if response contains API error even with returncode 0
            if response and "API Error:" in response:
                logger.error(f"API Error in response: {response}")
                if "max_tokens" in response and "thinking.budget_tokens" in response:
                    response = "エラー: ultrathink (32K)モードは現在のCLI実装の制限により使用できません。代わりにmegathink (10K)またはthink harder (20K)をお使いください。"
                else:
                    response = f"APIエラーが発生しました: {response}"
        else:
            logger.error(f"Claude error: {result.stderr}")
            error_msg = result.stderr.strip()
            # Also check stdout for error messages (Claude sometimes outputs errors to stdout)
            if not error_msg and result.stdout:
                stdout_lower = result.stdout.lower()
                if "api error" in stdout_lower or "error" in stdout_lower:
                    error_msg = result.stdout.strip()
            
            if "job was not started" in error_msg and ("payments have failed" in error_msg or "spending limit" in error_msg):
                response = "エラー: Anthropicアカウントの支払いに問題があります。'Billing & plans'セクションで支払い情報を確認してください。"
            elif "max_tokens" in error_msg and "thinking.budget_tokens" in error_msg:
                response = "エラー: ultrathink (32K)モードは現在のCLI実装の制限により使用できません。代わりにmegathink (10K)またはthink harder (20K)をお使いください。"
            elif "rate limit" in error_msg.lower():
                response = "エラー: レート制限に達しました。しばらくお待ちください。"
            else:
                response = f"申し訳ございません。エラーが発生しました: {error_msg[:200]}"
        
        return jsonify({
            "id": str(uuid.uuid4()),
            "message": response
        })
        
    except subprocess.TimeoutExpired:
        logger.error(f"Claude CLI timeout after {timeout} seconds")
        return jsonify({"error": "Request timeout", "message": "処理がタイムアウトしました。"}), 504
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        error_message = str(e)
        if "rate limit" in error_message.lower():
            return jsonify({"error": "Rate limit exceeded", "message": "レート制限に達しました。しばらくお待ちください。"}), 429
        return jsonify({"error": str(e), "message": "エラーが発生しました。"}), 500

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
        'sonnet4': 'claude-sonnet-4-20250514',  # Sonnet 4 specific
        # Keep full names as-is
        'claude-sonnet-4-20250514': 'claude-sonnet-4-20250514'
    }
    
    # Convert model name
    model = model_mapping.get(model, model)
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Escape problematic patterns that can cause CLI parsing issues
    escaped_message = message
    # Count quotes and add closing quote if odd number
    if escaped_message.count("'") % 2 == 1:
        escaped_message += "'"
    if escaped_message.count('"') % 2 == 1:
        escaped_message += '"'
    # Balance parentheses
    open_parens = escaped_message.count('(')
    close_parens = escaped_message.count(')')
    if open_parens > close_parens:
        escaped_message += ')' * (open_parens - close_parens)
    
    # Add safety prompt
    safe_prompt = (
        "重要: あなたは別のPCで作業中のユーザーを支援しています。"
        "このサーバーのファイルやコマンドを操作しないでください。"
        "質問に対してWeb検索や知識に基づいた回答のみを提供してください。"
        "検索結果を使用した場合は、必ず情報源のURLを明記してください。\n\n"
        f"ユーザーの質問: {escaped_message}"
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