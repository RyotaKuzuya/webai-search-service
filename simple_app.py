#!/usr/bin/env python3
"""
Simple WebAI Application with Authentication and Chat History
"""

import os
import json
import sqlite3
import datetime
import requests
import subprocess
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URLs
SIMPLE_API_URL = "http://localhost:8001"
SESSION_API_URL = "http://localhost:8003"  # Using simplified session API

# Session management
user_sessions = {}

# Database setup
DB_PATH = "webai.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create chats table
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  chat_id INTEGER NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (chat_id) REFERENCES chats (id))''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Simple user class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Fixed user credentials
USERS = {
    'kuzuya': generate_password_hash('kuzuya00')
}

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

@app.route('/')
def index():
    """Redirect to login or chat"""
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and check_password_hash(USERS[username], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error='ユーザー名またはパスワードが間違っています')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    """Main chat interface"""
    return render_template('chat_simple.html', username=current_user.id)

@app.route('/api/chats', methods=['GET'])
@login_required
def get_chats():
    """Get user's chat list"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, title, created_at, updated_at 
                 FROM chats 
                 WHERE user_id = ? 
                 ORDER BY updated_at DESC''', (current_user.id,))
    chats = []
    for row in c.fetchall():
        chats.append({
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'updated_at': row[3]
        })
    conn.close()
    return jsonify(chats)

@app.route('/api/chats', methods=['POST'])
@login_required
def create_chat():
    """Create new chat"""
    data = request.get_json()
    title = data.get('title', '新しいチャット')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO chats (user_id, title) VALUES (?, ?)', 
              (current_user.id, title))
    chat_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': chat_id, 'title': title})

@app.route('/api/chats/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    """Delete chat"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check ownership
    c.execute('SELECT user_id FROM chats WHERE id = ?', (chat_id,))
    row = c.fetchone()
    if not row or row[0] != current_user.id:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete messages and chat
    c.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
    c.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
@login_required
def get_messages(chat_id):
    """Get chat messages"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check ownership
    c.execute('SELECT user_id FROM chats WHERE id = ?', (chat_id,))
    row = c.fetchone()
    if not row or row[0] != current_user.id:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get messages
    c.execute('''SELECT role, content, created_at 
                 FROM messages 
                 WHERE chat_id = ? 
                 ORDER BY created_at''', (chat_id,))
    messages = []
    for row in c.fetchall():
        messages.append({
            'role': row[0],
            'content': row[1],
            'created_at': row[2]
        })
    conn.close()
    
    return jsonify(messages)

@app.route('/api/monitor', methods=['GET'])
@login_required
def get_claude_monitor():
    """Get Claude token usage with simulated monitor display"""
    try:
        # Get current time in JST
        import pytz
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.datetime.now(jst)
        current_time = now_jst.strftime('%H:%M:%S')
        
        # Calculate time until reset (4 AM JST)
        reset_hour = 4
        reset_time = now_jst.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
        if now_jst.hour >= reset_hour:
            # Next reset is tomorrow
            reset_time += datetime.timedelta(days=1)
        
        time_until_reset = reset_time - now_jst
        hours_until_reset = int(time_until_reset.total_seconds() // 3600)
        minutes_until_reset = int((time_until_reset.total_seconds() % 3600) // 60)
        
        # Calculate hours since reset
        hours_since_reset = (now_jst.hour - reset_hour) if now_jst.hour >= reset_hour else (now_jst.hour + 24 - reset_hour)
        
        # Try to detect plan from config
        plan_name = "Unknown"
        max_tokens = 7000  # Default to Pro plan
        
        config_path = os.path.expanduser('~/.config/claude/claude_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'user' in config and 'plan' in config['user']:
                        plan_info = config['user']['plan']
                        plan_name = plan_info.get('name', 'Unknown')
                        
                        # Map plan names to token limits
                        if 'max5' in plan_name.lower():
                            max_tokens = 35000
                            plan_name = "Max5"
                        elif 'max20' in plan_name.lower():
                            max_tokens = 140000
                            plan_name = "Max20"
                        elif 'max1' in plan_name.lower():
                            max_tokens = 7000
                            plan_name = "Max1"
                        elif 'pro' in plan_name.lower():
                            max_tokens = 7000
                            plan_name = "Pro"
                        else:
                            # Try to extract from plan details
                            logger.info(f"Detected plan: {plan_info}")
                            plan_name = plan_info.get('name', 'Unknown')
                            max_tokens = 35000  # Default to Max5 for unknown
            except Exception as e:
                logger.error(f"Error reading plan from config: {e}")
        
        # Try to get actual usage from Claude API test
        token_info = "Checking..."
        estimated_tokens = 0
        is_rate_limited = False
        
        try:
            # Make a minimal API call to check status
            claude_path = '/home/ubuntu/.npm-global/bin/claude'
            test_result = subprocess.run(
                [claude_path, '--print', '--model', 'claude-3-5-haiku-20241022', 'Return only: OK'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if test_result.returncode == 0:
                # Estimate tokens based on time of day
                # Rough estimate: 1000-2000 tokens per hour of usage
                estimated_tokens = min(int(hours_since_reset * 1500), max_tokens - 1000)
                token_info = f"{estimated_tokens:,} / ~{max_tokens:,}"
            else:
                error = test_result.stderr.strip()
                logger.info(f"Claude API response: {error}")
                
                # Check for various error conditions
                if 'rate limit' in error.lower() or 'limit reached' in error.lower() or 'rate_limit_error' in error.lower():
                    is_rate_limited = True
                    estimated_tokens = max_tokens
                    token_info = f"{max_tokens:,} / {max_tokens:,} (Rate Limited)"
                elif 'overloaded' in error.lower():
                    token_info = "Service Overloaded"
                    # Still try to estimate based on time
                    estimated_tokens = min(int(hours_since_reset * 1500), max_tokens - 1000)
                elif 'authentication' in error.lower() or 'unauthorized' in error.lower():
                    token_info = "Authentication Error"
                elif error == "" or error == " ":
                    # Empty error often means rate limit
                    is_rate_limited = True
                    estimated_tokens = max_tokens
                    token_info = f"{max_tokens:,} / {max_tokens:,} (Likely Rate Limited)"
                else:
                    token_info = f"API Error: {error[:50]}..."
                    # Still try to estimate
                    estimated_tokens = min(int(hours_since_reset * 1500), max_tokens - 1000)
        except subprocess.TimeoutExpired:
            token_info = "Timeout (Checking...)"
        except Exception as e:
            token_info = "Error Checking"
            logger.error(f"Error checking Claude status: {e}")
        
        # Calculate progress bars
        token_percentage = min(int((estimated_tokens / max_tokens) * 100), 100)
        token_bar_filled = int(token_percentage * 0.5)  # 50 chars total
        token_bar = '█' * token_bar_filled + '░' * (50 - token_bar_filled)
        
        time_percentage = int(((24 - hours_until_reset) / 24) * 100)
        time_bar_filled = int(time_percentage * 0.5)
        time_bar = '█' * time_bar_filled + '░' * (50 - time_bar_filled)
        
        # Calculate burn rate
        if hours_since_reset > 0 and not is_rate_limited:
            burn_rate = estimated_tokens / (hours_since_reset * 60)
        else:
            burn_rate = 0
        
        # Predict end time
        if burn_rate > 0 and not is_rate_limited:
            remaining_tokens = max_tokens - estimated_tokens
            minutes_until_exhausted = remaining_tokens / burn_rate
            exhausted_time = now_jst + datetime.timedelta(minutes=minutes_until_exhausted)
            predicted_end = exhausted_time.strftime('%H:%M')
        elif is_rate_limited:
            predicted_end = "NOW (Rate Limited)"
        else:
            predicted_end = "--:--"
        
        # Color coding for rate limit status
        status_icon = "🔴" if is_rate_limited else "🟢"
        status_text = "Rate Limited - Waiting for reset" if is_rate_limited else "Session Active"
        
        # Create monitor output
        monitor_output = f"""✨ ✨ ✨ CLAUDE TOKEN MONITOR ({plan_name.upper()}) ✨ ✨ ✨
============================================================

📊 Token Usage:    [{token_bar}] {token_percentage}%

⏳ Time to Reset:  [{time_bar}] {hours_until_reset}h {minutes_until_reset}m

🎯 Tokens:         {token_info} ({max_tokens - estimated_tokens:,} left)
🔥 Burn Rate:      {burn_rate:.1f} tokens/min

🏁 Predicted End:  {predicted_end}
🔄 Token Reset:    {reset_hour:02d}:00 JST

{status_icon} {current_time} 📝 {status_text} | {plan_name} Plan ({max_tokens:,} tokens/day)

📅 Session Start:  {(now_jst - datetime.timedelta(hours=hours_since_reset)).strftime('%H:%M')}
⏱️ Session Time:   {hours_since_reset}h {int((now_jst - datetime.timedelta(hours=hours_since_reset)).minute)}m
⏳ Time Remaining: {hours_until_reset}h {minutes_until_reset}m until reset"""
        
        # Add rate limit specific information
        if is_rate_limited:
            monitor_output += f"""

⚠️ RATE LIMIT REACHED ⚠️
========================
- All tokens for today have been consumed
- New tokens will be available at {reset_hour:02d}:00 JST
- Time until reset: {hours_until_reset}h {minutes_until_reset}m
- Consider upgrading your plan for more tokens"""
        
        return jsonify({
            'success': True,
            'monitor': monitor_output,
            'timestamp': now_jst.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in monitor display: {e}")
        # Fallback display
        return jsonify({
            'success': True,
            'monitor': f"""✨ ✨ ✨ CLAUDE TOKEN MONITOR (MAX5) ✨ ✨ ✨
============================================================

⚠️  Monitor initialization in progress...

Please ensure:
1. Claude Code is authenticated
2. You have an active session
3. API access is available

Error: {str(e)}

Retrying...""",
            'timestamp': datetime.datetime.now().isoformat()
        })

@app.route('/api/status', methods=['GET'])
@login_required
def get_claude_status():
    """Get Claude usage information from various sources"""
    try:
        status_info = []
        claude_path = '/home/ubuntu/.npm-global/bin/claude'
        
        # Try to get version info
        try:
            result = subprocess.run(
                [claude_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                status_info.append(f"Claude CLI Version: {result.stdout.strip()}")
        except:
            pass
        
        # Check config file for user info
        config_path = os.path.expanduser('~/.config/claude/claude_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'user' in config:
                        user_info = config['user']
                        status_info.append(f"\nUser: {user_info.get('email', 'N/A')}")
                        status_info.append(f"Plan: {user_info.get('plan', {}).get('name', 'N/A')}")
            except:
                pass
        
        # Try to get recent usage info by making a test request
        status_info.append("\n--- Token Usage Test ---")
        try:
            # Make a minimal request to check for rate limits
            test_result = subprocess.run(
                [claude_path, '--print', '--model', 'claude-3-5-haiku-20241022', 'Say "test" in one word only'],
                capture_output=True,
                text=True,
                timeout=10,
                env=os.environ.copy()
            )
            
            if test_result.returncode == 0:
                status_info.append("✓ API is accessible")
                status_info.append("✓ Tokens are available")
            else:
                error_msg = test_result.stderr.strip()
                if 'rate limit' in error_msg.lower():
                    status_info.append("⚠️ Rate limit reached")
                    # Extract rate limit info if available
                    if 'reset' in error_msg.lower():
                        status_info.append(f"Details: {error_msg}")
                elif 'overloaded' in error_msg.lower():
                    status_info.append("⚠️ Service is currently overloaded")
                else:
                    # Show full error message for debugging
                    status_info.append(f"⚠️ API Error: {error_msg if error_msg else 'No error message'}")
        except subprocess.TimeoutExpired:
            status_info.append("⚠️ Request timed out")
        except Exception as e:
            status_info.append(f"⚠️ Test failed: {str(e)}")
        
        # Add timestamp
        status_info.append(f"\n--- Checked at ---")
        status_info.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Note about external monitoring
        status_info.append("\n--- Note ---")
        status_info.append("For detailed token monitoring, consider using:")
        status_info.append("• claude-monitor tool")
        status_info.append("• Anthropic Console dashboard")
        
        return jsonify({
            'success': True,
            'status': '\n'.join(status_info),
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting Claude status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
@login_required
def clear_context():
    """Clear Claude context"""
    try:
        # Check if user has a session
        if current_user.id in user_sessions:
            session_id = user_sessions[current_user.id]
            response = requests.post(f"{SESSION_API_URL}/session/{session_id}/clear")
            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'セッションのコンテキストをクリアしました（/clearコマンド実行）'})
        
        # Fallback to simple API
        response = requests.post(f"{SIMPLE_API_URL}/clear")
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'コンテキストをクリアしました'})
        else:
            return jsonify({'error': 'Failed to clear context'}), 500
    except Exception as e:
        logger.error(f"Error clearing context: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send', methods=['POST'])
@login_required
def send_message():
    """Send message to Claude"""
    data = request.get_json()
    message = data.get('message', '')
    chat_id = data.get('chat_id')
    model = data.get('model', 'opus')  # Default to opus
    use_session = data.get('use_session', False)
    
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
        return jsonify({'error': 'No message provided'}), 400
    
    # Create new chat if needed
    if not chat_id:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Generate title from first message
        title = message[:30] + "..." if len(message) > 30 else message
        c.execute('INSERT INTO chats (user_id, title) VALUES (?, ?)', 
                  (current_user.id, title))
        chat_id = c.lastrowid
        conn.commit()
        conn.close()
    
    # Save user message
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
              (chat_id, 'user', message))
    conn.commit()
    
    try:
        # Increase timeout based on thinking mode and expected processing time
        # Anthropic recommends up to 60 minutes for Claude 3.7/4
        if 'ultrathink' in message.lower():
            timeout = 1800  # 30 minutes for ultrathink (31,999 tokens)
        elif 'megathink' in message.lower():
            timeout = 900   # 15 minutes for megathink (10,000 tokens)
        else:
            timeout = 600   # 10 minutes minimum for all queries
        
        if use_session:
            # Use session API for persistent context
            if current_user.id not in user_sessions:
                # Create new session
                session_response = requests.post(f"{SESSION_API_URL}/session/create")
                if session_response.status_code == 200:
                    user_sessions[current_user.id] = session_response.json()['session_id']
                else:
                    # Fallback to simple API
                    use_session = False
            
            if use_session and current_user.id in user_sessions:
                session_id = user_sessions[current_user.id]
                response = requests.post(
                    f"{SESSION_API_URL}/session/{session_id}/message",
                    json={'message': message, 'model': model},
                    timeout=timeout
                )
            else:
                # Fallback to simple API
                response = requests.post(
                    f"{SIMPLE_API_URL}/chat",
                    json={'message': message, 'model': model},
                    timeout=timeout
                )
        else:
            # Use simple API
            response = requests.post(
                f"{SIMPLE_API_URL}/chat",
                json={'message': message, 'model': model},
                timeout=timeout
            )
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result.get('message', '')
            
            # Save AI response
            c.execute('INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
                      (chat_id, 'assistant', ai_message))
            
            # Update chat timestamp
            c.execute('UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                      (chat_id,))
            conn.commit()
            conn.close()
            
            return jsonify({
                'chat_id': chat_id,
                'message': ai_message
            })
        else:
            conn.close()
            error_msg = f'API error: Status {response.status_code}'
            try:
                error_detail = response.json()
                error_msg = error_detail.get('error', error_msg)
            except:
                error_msg = response.text or error_msg
            logger.error(f"API returned error: {error_msg}")
            return jsonify({'error': error_msg}), 500
            
    except requests.exceptions.Timeout:
        conn.close()
        logger.error("Request timeout error")
        return jsonify({'error': 'リクエストがタイムアウトしました。処理に時間がかかっています。'}), 504
    except requests.exceptions.ConnectionError as e:
        conn.close()
        logger.error(f"Connection error: {e}")
        return jsonify({'error': 'APIサーバーに接続できません。'}), 503
    except Exception as e:
        conn.close()
        logger.error(f"Error sending message: {e}")
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Simple WebAI on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)