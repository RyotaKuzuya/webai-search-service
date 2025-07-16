#!/usr/bin/env python3
"""
WebAI Search Service - Main Application
"""
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os
import sys
import json
import time
from datetime import datetime
import secrets
import queue
import re
from dotenv import load_dotenv
from session_manager import SessionManager
from config import DB_PATH, APP_LOG

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize session manager
# Use external HDD for database storage
session_manager = SessionManager(DB_PATH)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 管理者アカウント (環境変数から取得)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secure_password_123')

# Claude実行パス
CLAUDE_EXECUTABLE = os.environ.get('CLAUDE_EXECUTABLE', 'claude')

class ClaudeRunner:
    def __init__(self, socketio, session_id):
        self.socketio = socketio
        self.session_id = session_id
        self.process = None
        self.output_queue = queue.Queue()
        
    def run_query(self, prompt):
        """Claudeコマンドを実行してプロンプトを処理"""
        try:
            # Web検索機能を明示的に有効にするプロンプトを構築
            enhanced_prompt = f"""あなたはWeb検索機能を持つAIアシスタントです。
必要に応じてWebSearch toolを使用して、最新の情報や特定のWebサイトの内容を検索してください。

ユーザーの質問: {prompt}

この質問に答える際、以下の点に注意してください：
1. 最新の情報が必要な場合は、WebSearch toolを使用して検索を実行
2. 特定のWebサイトについて聞かれた場合は、そのサイトの内容を検索
3. 検索結果を元に、正確で有用な回答を提供"""
            
            # Claudeコマンドを構築
            cmd = [CLAUDE_EXECUTABLE, enhanced_prompt]
            
            # プロセスを開始
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            
            # 出力を読み取るスレッドを開始
            read_thread = threading.Thread(target=self._read_output)
            read_thread.daemon = True
            read_thread.start()
            
            # 出力をリアルタイムで送信
            accumulated_output = []
            while True:
                try:
                    line = self.output_queue.get(timeout=0.1)
                    if line is None:  # プロセス終了
                        break
                    
                    accumulated_output.append(line)
                    
                    # 特定のパターンを検出して進捗を表示
                    if "WebSearch" in line or "searching" in line.lower():
                        self.socketio.emit('stream_update', {
                            'type': 'progress',
                            'content': f"🔍 {line}",
                            'timestamp': datetime.now().isoformat()
                        }, room=self.session_id)
                    elif "WebFetch" in line or "fetching" in line.lower():
                        self.socketio.emit('stream_update', {
                            'type': 'progress',
                            'content': f"📄 {line}",
                            'timestamp': datetime.now().isoformat()
                        }, room=self.session_id)
                    else:
                        # 通常の出力を蓄積して表示
                        current_content = '\n'.join(accumulated_output)
                        self.socketio.emit('stream_update', {
                            'type': 'assistant',
                            'content': current_content,
                            'timestamp': datetime.now().isoformat()
                        }, room=self.session_id)
                    
                except queue.Empty:
                    if self.process.poll() is not None:
                        # プロセスが終了している
                        break
            
            # 最終的な結果を送信
            if self.process.returncode == 0:
                self.socketio.emit('stream_update', {
                    'type': 'complete',
                    'content': '\n'.join(accumulated_output),
                    'timestamp': datetime.now().isoformat()
                }, room=self.session_id)
            else:
                self.socketio.emit('stream_update', {
                    'type': 'error',
                    'content': f'Process exited with code {self.process.returncode}',
                    'timestamp': datetime.now().isoformat()
                }, room=self.session_id)
                
        except Exception as e:
            self.socketio.emit('stream_update', {
                'type': 'error',
                'content': str(e),
                'timestamp': datetime.now().isoformat()
            }, room=self.session_id)
    
    def _read_output(self):
        """出力を読み取ってキューに追加"""
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_queue.put(line.strip())
            self.output_queue.put(None)  # 終了シグナル
        except Exception as e:
            self.output_queue.put(f"Error reading output: {e}")

@app.route('/')
def index():
    """メインページ"""
    if 'username' not in session:
        return render_template('login.html')
    return redirect('/chat')

@app.route('/chat')
def chat():
    """チャットページ"""
    if 'username' not in session:
        return redirect('/login')
    return render_template('chat_simple.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン処理"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 複数の認証情報をサポート
        valid_credentials = [
            (ADMIN_USERNAME, ADMIN_PASSWORD),
            ('kuzuya', 'kuzuya00')
        ]
        
        if any(username == u and password == p for u, p in valid_credentials):
            session['username'] = username
            return redirect('/chat')
        else:
            return render_template('login.html', error='ユーザー名またはパスワードが間違っています')
    
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    # 複数の認証情報をサポート
    valid_credentials = [
        (ADMIN_USERNAME, ADMIN_PASSWORD),
        ('kuzuya', 'kuzuya00')
    ]
    
    if any(username == u and password == p for u, p in valid_credentials):
        session['username'] = username
        return jsonify({'success': True, 'username': username})
    else:
        return jsonify({'success': False, 'error': 'ユーザー名またはパスワードが間違っています'}), 401

@app.route('/logout')
def logout():
    """ログアウト処理"""
    session.pop('username', None)
    return redirect('/')

@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get user's chat list"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['username']
    chats = session_manager.get_user_chats(user_id)
    return jsonify(chats)

@app.route('/api/send', methods=['POST'])
def api_send():
    """Send message API endpoint"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    chat_id = data.get('chat_id')
    model = data.get('model', 'opus')
    use_session = data.get('use_session', False)
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    user_id = session['username']
    
    # Create new chat if needed
    if not chat_id:
        chat_id = session_manager.create_chat(user_id)
    
    # Save user message
    session_manager.add_message(chat_id, 'user', message)
    
    try:
        # Build conversation history if session mode is enabled
        conversation_history = []
        if use_session:
            conversation_history = session_manager.build_conversation_history(chat_id)
            # Remove the last message (current one) to avoid duplication
            if conversation_history and conversation_history[-1]['content'] == message:
                conversation_history = conversation_history[:-1]
        
        # Prepare the full prompt with history
        full_prompt = message
        if conversation_history:
            # Format conversation history
            history_text = ""
            for msg in conversation_history:
                role = "ユーザー" if msg['role'] == 'user' else "アシスタント"
                history_text += f"\n{role}: {msg['content']}\n"
            
            full_prompt = f"以下は過去の会話履歴です:\n{history_text}\n\n現在のユーザーの質問: {message}"
        
        # Use simple API for now
        import requests
        api_url = "http://localhost:8001/chat"
        response = requests.post(
            api_url,
            json={'message': full_prompt, 'model': model},
            timeout=600
        )
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result.get('message', '')
            
            # Save assistant response
            if assistant_message:
                session_manager.add_message(chat_id, 'assistant', assistant_message)
            
            return jsonify({
                'message': assistant_message,
                'chat_id': chat_id
            })
        else:
            return jsonify({'error': 'API error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def api_clear():
    """Clear context API endpoint"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['username']
    session_manager.clear_session_context(user_id)
    
    return jsonify({'success': True, 'message': 'コンテキストをクリアしました'})

@app.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    """Get messages for a specific chat"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    messages = session_manager.get_chat_messages(chat_id)
    return jsonify(messages)

@app.route('/api/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    session_manager.delete_chat(chat_id)
    return jsonify({'success': True})

@app.route('/api/monitor', methods=['GET'])
def api_monitor():
    """Get Claude monitor status"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Simple monitor display
        monitor_output = """✨ ✨ ✨ CLAUDE TOKEN MONITOR ✨ ✨ ✨
============================================================

📊 Token Usage:    [████████████████████░░░░░░░░░░░░░░░░░░░░] 50%

⏳ Time to Reset:  [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 30%

🎯 Tokens:         70,000 / 140,000 (70,000 left)
🔥 Burn Rate:      100 tokens/min

🏁 Predicted End:  23:00
🔄 Token Reset:    04:00 JST

🟢 Session Active | Max20 Plan (140,000 tokens/day)"""
        
        return jsonify({
            'success': True,
            'monitor': monitor_output,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
    session_id = data.get('session_id', request.sid)
    
    # バックグラウンドでClaudeを実行
    runner = ClaudeRunner(socketio, session_id)
    thread = threading.Thread(target=runner.run_query, args=(prompt,))
    thread.daemon = True
    thread.start()
    
    emit('query_started', {'status': 'Processing your query...'})

if __name__ == '__main__':
    # 必要なディレクトリを作成
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, allow_unsafe_werkzeug=True)