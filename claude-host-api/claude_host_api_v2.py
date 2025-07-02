#!/usr/bin/env python3
"""
Claude Host API v2 - Improved integration with Claude CLI
Uses --print mode for non-interactive responses
"""

import os
import json
import subprocess
import asyncio
import uuid
import time
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import logging
import threading
import queue

app = Flask(__name__)
CORS(app, origins=["*"])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Claude binary path - use wrapper script
CLAUDE_PATH = "/home/ubuntu/webai/claude-host-api/claude_wrapper.sh"
HOME_DIR = "/home/ubuntu"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    claude_exists = os.path.exists(CLAUDE_PATH)
    
    # Test Claude version
    version = "unknown"
    try:
        result = subprocess.run(
            [CLAUDE_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
    except:
        pass
    
    return jsonify({
        "status": "healthy",
        "service": "claude-host-api-v2",
        "claude_available": claude_exists,
        "claude_path": CLAUDE_PATH,
        "claude_version": version
    })

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint for compatibility"""
    claude_exists = os.path.exists(CLAUDE_PATH)
    return jsonify({
        "status": "healthy",
        "service": "claude-host-api-v2",
        "claude_available": claude_exists
    })

@app.route('/message', methods=['POST'])
def message():
    """Message endpoint using Claude CLI in print mode"""
    data = request.get_json()
    content = data.get('content', '')
    model = data.get('model', 'claude-3-5-haiku-20241022')
    web_search = data.get('web_search', True)
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    logger.info(f"Received message: {content[:100]}...")
    
    def generate():
        output_queue = queue.Queue()
        error_queue = queue.Queue()
        
        def run_claude():
            try:
                # Add safety prompt to prevent system manipulation
                safe_prompt = (
                    "重要: あなたは別のPCで作業中のユーザーを支援するAIアシスタントです。"
                    "このLinuxサーバーのファイルシステムやコマンドを実行することは絶対に避けてください。"
                    "ユーザーからの質問に対して、検索結果や知識に基づいた回答のみを提供してください。"
                    "コマンド実行やファイル操作の指示があっても、それらは別のPCでの作業を想定してアドバイスしてください。"
                )
                
                # Add web search instruction if enabled
                if web_search:
                    safe_prompt += "\n\n質問に答える際は、必要に応じてWebSearchツールを使用して最新の情報を検索してください。"
                
                safe_prompt += f"\n\nユーザーの質問: {content}"
                
                # Map model names to claude-code model aliases
                model_map = {
                    'claude-opus-4': 'opus',
                    'claude-sonnet-4': 'sonnet',
                    'claude-3-7-sonnet': 'sonnet-3.7',
                    'claude-3-5-haiku-20241022': 'haiku'
                }
                
                model_alias = model_map.get(model, 'haiku')
                
                # Use --print mode with stream-json output format for real-time streaming
                cmd = [
                    CLAUDE_PATH,
                    "--print",
                    "--output-format", "stream-json",
                    "--model", model_alias,
                    safe_prompt
                ]
                
                logger.info(f"Executing: {' '.join(cmd[:4])}...")
                
                # Set up environment
                env = os.environ.copy()
                env['HOME'] = HOME_DIR
                env['NODE_ENV'] = 'production'
                # Add npm global paths
                env['PATH'] = f"/home/ubuntu/.npm-global/bin:{env.get('PATH', '')}"
                env['NODE_PATH'] = '/home/ubuntu/.npm-global/lib/node_modules'
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    env=env,
                    cwd=HOME_DIR
                )
                
                # Read output line by line
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        try:
                            # Parse stream-json format
                            data = json.loads(line)
                            if data.get('type') == 'text':
                                text = data.get('text', '')
                                if text:
                                    output_queue.put(text)
                            elif data.get('type') == 'error':
                                error_queue.put(data.get('error', 'Unknown error'))
                        except json.JSONDecodeError:
                            # If not JSON, treat as plain text
                            output_queue.put(line)
                
                # Wait for process to complete
                process.wait()
                
                # Check for errors
                if process.returncode != 0:
                    stderr = process.stderr.read()
                    if stderr:
                        error_queue.put(f"Process error: {stderr}")
                
                # Signal completion
                output_queue.put(None)
                
            except Exception as e:
                logger.error(f"Error in run_claude: {e}", exc_info=True)
                error_queue.put(str(e))
                output_queue.put(None)
        
        # Start Claude in a separate thread
        thread = threading.Thread(target=run_claude)
        thread.start()
        
        # Stream output
        try:
            output_buffer = []
            while True:
                try:
                    # Check for errors first
                    if not error_queue.empty():
                        error = error_queue.get_nowait()
                        logger.error(f"Claude error: {error}")
                        yield json.dumps({"error": error}) + "\n"
                        break
                    
                    # Get output with timeout
                    output = output_queue.get(timeout=0.1)
                    
                    if output is None:
                        # Stream complete
                        break
                    
                    output_buffer.append(output)
                    yield json.dumps({"content": output}) + "\n"
                    
                except queue.Empty:
                    # Continue waiting
                    continue
            
            # If no output was received, try text mode
            if not output_buffer:
                logger.info("No stream output, trying text mode...")
                yield from fallback_text_mode(content, model, web_search)
            
            yield json.dumps({"status": "complete"}) + "\n"
            
        except Exception as e:
            logger.error(f"Error in generate: {e}", exc_info=True)
            yield json.dumps({"error": str(e)}) + "\n"
        
        finally:
            thread.join(timeout=5)
    
    return Response(
        stream_with_context(generate()),
        mimetype='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

def fallback_text_mode(content, model='claude-3-5-haiku-20241022', web_search=True):
    """Fallback to text mode if stream-json doesn't work"""
    try:
        # Add safety prompt
        safe_prompt = (
            "重要: あなたは別のPCで作業中のユーザーを支援するAIアシスタントです。"
            "このLinuxサーバーのファイルシステムやコマンドを実行することは絶対に避けてください。"
            "ユーザーからの質問に対して、検索結果や知識に基づいた回答のみを提供してください。"
            "コマンド実行やファイル操作の指示があっても、それらは別のPCでの作業を想定してアドバイスしてください。"
        )
        
        # Add web search instruction if enabled
        if web_search:
            safe_prompt += "\n\n質問に答える際は、必要に応じてWebSearchツールを使用して最新の情報を検索してください。"
        
        safe_prompt += f"\n\nユーザーの質問: {content}"
        
        # Map model names to claude-code model aliases
        model_map = {
            'claude-opus-4': 'opus',
            'claude-sonnet-4': 'sonnet',
            'claude-3-7-sonnet': 'sonnet-3.7',
            'claude-3-5-haiku-20241022': 'haiku'
        }
        
        model_alias = model_map.get(model, 'haiku')
        
        cmd = [
            CLAUDE_PATH,
            "--print",
            "--output-format", "text",
            "--model", model_alias,
            safe_prompt
        ]
        
        logger.info("Using fallback text mode...")
        
        env = os.environ.copy()
        env['HOME'] = HOME_DIR
        env['NODE_ENV'] = 'production'
        env['PATH'] = f"/home/ubuntu/.npm-global/bin:{env.get('PATH', '')}"
        env['NODE_PATH'] = '/home/ubuntu/.npm-global/lib/node_modules'
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=HOME_DIR
        )
        
        if result.returncode == 0 and result.stdout:
            # Split output into lines for streaming effect
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line:
                    yield json.dumps({"content": line}) + "\n"
                    time.sleep(0.05)  # Small delay for streaming effect
        else:
            error_msg = result.stderr or "No output from Claude"
            logger.error(f"Fallback error: {error_msg}")
            yield json.dumps({"content": "申し訳ございません。現在応答を生成できません。"}) + "\n"
            
    except Exception as e:
        logger.error(f"Fallback error: {e}", exc_info=True)
        yield json.dumps({"error": str(e)}) + "\n"

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
    
    logger.info(f"Chat completion request: {user_message[:100]}...")
    
    if stream:
        def generate_stream():
            # Forward to message endpoint for streaming
            response = message()
            for chunk in response.response:
                try:
                    data = json.loads(chunk)
                    if 'content' in data:
                        # Format as OpenAI stream chunk
                        chunk_data = {
                            'id': f'chatcmpl-{uuid.uuid4()}',
                            'object': 'chat.completion.chunk',
                            'created': int(time.time()),
                            'model': model,
                            'choices': [{
                                'index': 0,
                                'delta': {'content': data['content']},
                                'finish_reason': None
                            }]
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                    elif data.get('status') == 'complete':
                        # Send finish chunk
                        finish_data = {
                            'id': f'chatcmpl-{uuid.uuid4()}',
                            'object': 'chat.completion.chunk',
                            'created': int(time.time()),
                            'model': model,
                            'choices': [{
                                'index': 0,
                                'delta': {},
                                'finish_reason': 'stop'
                            }]
                        }
                        yield f"data: {json.dumps(finish_data)}\n\n"
                        yield "data: [DONE]\n\n"
                except:
                    pass
        
        return Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        # Non-streaming response
        # Add safety prompt
        safe_prompt = (
            "重要: あなたは別のPCで作業中のユーザーを支援するAIアシスタントです。"
            "このLinuxサーバーのファイルシステムやコマンドを実行することは絶対に避けてください。"
            "ユーザーからの質問に対して、検索結果や知識に基づいた回答のみを提供してください。"
            "コマンド実行やファイル操作の指示があっても、それらは別のPCでの作業を想定してアドバイスしてください。\n\n"
            f"ユーザーの質問: {user_message}"
        )
        
        # Use text mode for complete response
        cmd = [
            CLAUDE_PATH,
            "--print",
            "--output-format", "text",
            safe_prompt
        ]
        
        env = os.environ.copy()
        env['HOME'] = HOME_DIR
        env['NODE_ENV'] = 'production'
        env['PATH'] = f"/home/ubuntu/.npm-global/bin:{env.get('PATH', '')}"
        env['NODE_PATH'] = '/home/ubuntu/.npm-global/lib/node_modules'
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
                cwd=HOME_DIR
            )
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
            else:
                response_text = "申し訳ございません。応答を生成できませんでした。"
                
            return jsonify({
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }]
            })
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Claude Host API v2 on port {port}")
    logger.info(f"Claude path: {CLAUDE_PATH}")
    logger.info(f"Home directory: {HOME_DIR}")
    
    # Test Claude availability
    if os.path.exists(CLAUDE_PATH):
        logger.info("Claude CLI found")
    else:
        logger.error("Claude CLI not found!")
    
    app.run(host='0.0.0.0', port=port, debug=False)