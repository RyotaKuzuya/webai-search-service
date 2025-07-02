#!/usr/bin/env python3
"""
WebAI Search Service - Claude Code API Integration
Uses claude-code-api instead of direct CLI calls
"""
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import requests
import json
import os
import time
from datetime import datetime
import secrets
import threading
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 管理者アカウント (環境変数から取得)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secure_password_123')

# Claude API設定
CLAUDE_API_URL = os.environ.get('CLAUDE_API_URL', 'http://localhost:8000')
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')  # オプション：APIキーが必要な場合

# 利用可能なモデル
AVAILABLE_MODELS = [
    'claude-opus-4-20250514',
    'claude-sonnet-4-20250514',
    'claude-3-7-sonnet-20250219',
    'claude-3-5-haiku-20241022'
]

DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'claude-opus-4-20250514')

class ClaudeAPIRunner:
    def __init__(self, socketio, session_id):
        self.socketio = socketio
        self.session_id = session_id
        
    def run_query(self, prompt, model=None):
        """Claude Code APIを使用してプロンプトを処理"""
        try:
            # モデルの選択
            selected_model = model or DEFAULT_MODEL
            
            # Web検索機能を明示的に有効にするプロンプトを構築
            enhanced_prompt = f"""あなたはWeb検索機能を持つAIアシスタントです。
必要に応じてWebSearch toolを使用して、最新の情報や特定のWebサイトの内容を検索してください。

ユーザーの質問: {prompt}

この質問に答える際、以下の点に注意してください：
1. 最新の情報が必要な場合は、WebSearch toolを使用して検索を実行
2. 特定のWebサイトについて聞かれた場合は、そのサイトの内容を検索
3. 検索結果を元に、正確で有用な回答を提供"""
            
            # APIリクエストのヘッダー
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            }
            
            # APIキーが設定されている場合は追加
            if CLAUDE_API_KEY:
                headers['Authorization'] = f'Bearer {CLAUDE_API_KEY}'
            
            # リクエストボディ
            data = {
                'model': selected_model,
                'messages': [
                    {'role': 'user', 'content': enhanced_prompt}
                ],
                'stream': True,
                'temperature': 0.7,
                'max_tokens': 4096
            }
            
            # ストリーミングレスポンスを送信
            self.socketio.emit('stream_update', {
                'type': 'info',
                'content': f'🤖 Using model: {selected_model}',
                'timestamp': datetime.now().isoformat()
            }, room=self.session_id)
            
            # APIリクエストを送信
            response = requests.post(
                f'{CLAUDE_API_URL}/v1/chat/completions',
                headers=headers,
                json=data,
                stream=True,
                timeout=300
            )
            
            if response.status_code != 200:
                raise Exception(f'API returned status code {response.status_code}: {response.text}')
            
            # ストリーミングレスポンスを処理
            accumulated_content = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    accumulated_content.append(content)
                                    
                                    # 特定のパターンを検出して進捗を表示
                                    if "WebSearch" in content or "searching" in content.lower():
                                        self.socketio.emit('stream_update', {
                                            'type': 'progress',
                                            'content': f"🔍 Searching...",
                                            'timestamp': datetime.now().isoformat()
                                        }, room=self.session_id)
                                    elif "WebFetch" in content or "fetching" in content.lower():
                                        self.socketio.emit('stream_update', {
                                            'type': 'progress',
                                            'content': f"📄 Fetching content...",
                                            'timestamp': datetime.now().isoformat()
                                        }, room=self.session_id)
                                    
                                    # 通常の出力を送信
                                    current_content = ''.join(accumulated_content)
                                    self.socketio.emit('stream_update', {
                                        'type': 'assistant',
                                        'content': current_content,
                                        'timestamp': datetime.now().isoformat()
                                    }, room=self.session_id)
                        except json.JSONDecodeError:
                            continue
            
            # 完了通知
            self.socketio.emit('stream_update', {
                'type': 'complete',
                'content': ''.join(accumulated_content),
                'timestamp': datetime.now().isoformat()
            }, room=self.session_id)
                
        except requests.exceptions.Timeout:
            self.socketio.emit('stream_update', {
                'type': 'error',
                'content': 'Request timed out after 5 minutes',
                'timestamp': datetime.now().isoformat()
            }, room=self.session_id)
        except Exception as e:
            self.socketio.emit('stream_update', {
                'type': 'error',
                'content': str(e),
                'timestamp': datetime.now().isoformat()
            }, room=self.session_id)

@app.route('/')
def index():
    """メインページ"""
    if 'username' not in session:
        return render_template('login.html')
    return render_template('chat.html', 
                         username=session['username'],
                         models=AVAILABLE_MODELS,
                         default_model=DEFAULT_MODEL)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン処理"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """ログアウト処理"""
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/models')
def get_models():
    """利用可能なモデルのリストを返す"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'models': AVAILABLE_MODELS,
        'default': DEFAULT_MODEL
    })

@app.route('/api/health')
def health_check():
    """Claude Code APIの状態を確認"""
    try:
        response = requests.get(f'{CLAUDE_API_URL}/health', timeout=5)
        return jsonify({
            'api_status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'api_url': CLAUDE_API_URL
        })
    except:
        return jsonify({
            'api_status': 'unreachable',
            'api_url': CLAUDE_API_URL
        }), 503

@socketio.on('connect')
def handle_connect():
    """WebSocket接続時の処理"""
    if 'username' not in session:
        return False
    emit('connected', {'status': 'Connected to server'})

@socketio.on('join')
def handle_join(data):
    """セッションへの参加"""
    session_id = data.get('session_id', request.sid)
    socketio.server.manager.rooms['/'][request.sid].add(session_id)
    emit('joined', {'session_id': session_id})

@socketio.on('submit_query')
def handle_query(data):
    """クエリの実行"""
    if 'username' not in session:
        emit('error', {'error': 'Not authenticated'})
        return
    
    prompt = data.get('prompt', '')
    model = data.get('model', DEFAULT_MODEL)
    session_id = data.get('session_id', request.sid)
    
    # バックグラウンドでClaude APIを実行
    runner = ClaudeAPIRunner(socketio, session_id)
    thread = threading.Thread(target=runner.run_query, args=(prompt, model))
    thread.daemon = True
    thread.start()
    
    emit('query_started', {'status': 'Processing your query...', 'model': model})

if __name__ == '__main__':
    # 必要なディレクトリを作成
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    socketio.run(app, host='127.0.0.1', port=5001, debug=True, allow_unsafe_werkzeug=True)