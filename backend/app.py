import os
import uuid
import logging
import json
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CORS configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Patch DNS resolution for eventlet
import eventlet
eventlet.monkey_patch()

# SocketIO configuration
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=120,
    ping_interval=25,
    max_http_buffer_size=1000000
)

# Admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secure_password_123')

# Claude API URL - Use host.docker.internal when running in Docker
CLAUDE_API_URL = os.environ.get('CLAUDE_API_URL', 'http://host.docker.internal:8000')

# Active sessions tracking
active_sessions = {}


def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Main page - redirect to login or chat"""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')


@app.route('/chat')
@login_required
def chat():
    """Chat interface page"""
    return render_template('chat.html', username=session.get('username', 'Admin'))


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login API request"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['user_id'] = str(uuid.uuid4())
        session['username'] = username
        session.permanent = True
        
        logger.info(f"User {username} logged in successfully")
        return jsonify({'success': True, 'username': username})
    
    logger.warning(f"Failed login attempt for username: {username}")
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """Handle logout API request"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User {username} logged out")
    return jsonify({'success': True})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check Claude API availability
        claude_status = "unavailable"
        try:
            response = requests.get(f"{CLAUDE_API_URL}/status", timeout=5)
            if response.status_code == 200:
                claude_status = "available"
        except:
            pass
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'claude_api': claude_status,
            'active_sessions': len(active_sessions)
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"WebSocket connection attempt from {request.remote_addr}")
    logger.info(f"Session data: {dict(session)}")
    logger.info(f"Request SID: {request.sid}")
    
    # Check authentication manually for WebSocket
    if 'user_id' not in session:
        logger.warning(f"WebSocket connection rejected - no session: {request.sid}")
        return False
    
    session_id = session.get('user_id')
    if session_id:
        active_sessions[request.sid] = {
            'user_id': session_id,
            'username': session.get('username', 'Unknown'),
            'connected_at': datetime.utcnow()
        }
        logger.info(f"WebSocket connected successfully: {request.sid} for user {session.get('username')}")
        emit('connected', {'status': 'Connected to WebAI'})
    else:
        logger.error("Session ID exists but is empty")
        disconnect()


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    if request.sid in active_sessions:
        del active_sessions[request.sid]
        logger.info(f"WebSocket disconnected: {request.sid}")


@socketio.on('ping')
def handle_ping(data):
    """Handle ping for testing"""
    logger.info(f"Received ping: {data}")
    emit('pong', {'timestamp': data.get('timestamp'), 'server_time': datetime.utcnow().isoformat()})

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat message"""
    logger.info(f"[MESSAGE] Received message event from {request.sid}")
    logger.info(f"[MESSAGE] Data received: {data}")
    logger.info(f"[MESSAGE] Session info: user_id={session.get('user_id')}, username={session.get('username')}")
    
    # Check authentication
    if 'user_id' not in session:
        logger.error(f"[MESSAGE] No user_id in session for {request.sid}")
        emit('error', {'error': 'Authentication required'})
        return
    
    try:
        user_message = data.get('message', '')
        model = data.get('model', 'claude-3-sonnet')
        web_search = data.get('web_search', True)
        session_id = session.get('user_id')
        
        if not user_message:
            logger.error("[MESSAGE] Empty message received")
            emit('error', {'error': 'Empty message'})
            return
        
        logger.info(f"[MESSAGE] Processing: message='{user_message[:50]}...', model={model}, web_search={web_search}")
        
        # Emit acknowledgment
        emit('message_received', {'status': 'Processing your request...'})
        
        # Prepare request for Claude API
        claude_request = {
            'message': user_message,
            'model': model,
            'stream': True,
            'web_search': web_search
        }
        
        # Send request to Claude API
        try:
            # Check API availability first
            logger.info(f"Checking Claude API health at {CLAUDE_API_URL}/health")
            health_check = requests.get(f"{CLAUDE_API_URL}/health", timeout=5)
            if health_check.status_code != 200:
                logger.error(f"Claude API health check failed: {health_check.status_code}")
                emit('error', {'error': 'Claude API is not available'})
                return
            logger.info("Claude API health check passed")
            
            # Send message to Claude API with model and web_search parameters
            api_request = {
                'content': user_message,
                'model': model,
                'web_search': web_search
            }
            
            logger.info(f"[CLAUDE] Sending request to Claude API: {api_request}")
            logger.info(f"[CLAUDE] URL: {CLAUDE_API_URL}/message")
            
            response = requests.post(
                f"{CLAUDE_API_URL}/message",
                json=api_request,
                stream=True,
                timeout=120,
                headers={'Accept': 'application/x-ndjson'}
            )
            
            logger.info(f"Claude API response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Claude API error response: {response.text}")
                emit('error', {'error': f'Claude API error: {response.status_code}'})
                return
            
            # Stream response chunks
            current_content = ""
            chunk_count = 0
            logger.info("[STREAM] Starting to stream response chunks")
            
            for line in response.iter_lines():
                if line:
                    try:
                        line_str = line.decode('utf-8')
                        logger.debug(f"[STREAM] Raw line {chunk_count}: {line_str[:100]}")
                        
                        # Parse JSON lines
                        if line_str.strip():
                            data = json.loads(line_str)
                            logger.debug(f"[STREAM] Parsed data: {data}")
                            
                            if 'content' in data:
                                chunk_content = data['content']
                                if current_content:
                                    current_content += "\n" + chunk_content
                                else:
                                    current_content = chunk_content
                                
                                chunk_count += 1
                                logger.info(f"[STREAM] Emitting chunk {chunk_count}: {len(chunk_content)} chars to {request.sid}")
                                emit('stream_chunk', {'chunk': current_content})
                                
                            elif 'error' in data:
                                logger.error(f"[STREAM] Error from Claude API: {data['error']}")
                                emit('error', {'error': data['error']})
                                return
                                
                            elif 'status' in data and data['status'] == 'complete':
                                logger.info(f"[STREAM] Stream complete after {chunk_count} chunks")
                                emit('stream_complete', {'status': 'Response complete'})
                                break
                                
                    except json.JSONDecodeError as e:
                        logger.error(f"[STREAM] JSON decode error: {e}, line: {line_str}")
                    except Exception as e:
                        logger.error(f"[STREAM] Error parsing chunk: {e}")
            
            logger.info(f"[STREAM] Final: Sent {chunk_count} chunks, total content length: {len(current_content)}")
            emit('stream_complete', {'status': 'Response complete'})
            
        except requests.exceptions.Timeout:
            logger.error("[CLAUDE] Request timed out")
            emit('error', {'error': 'Request timed out'})
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[CLAUDE] Connection error: {e}")
            emit('error', {'error': 'Claude API is not available'})
        except Exception as e:
            logger.error(f"[CLAUDE] Request failed: {type(e).__name__}: {e}")
            emit('error', {'error': f'Failed to connect to Claude API: {str(e)}'})
            
    except Exception as e:
        logger.error(f"[MESSAGE] Error handling message: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"[MESSAGE] Traceback: {traceback.format_exc()}")
        emit('error', {'error': 'Internal server error'})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting WebAI on port {port} (debug={debug})")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)