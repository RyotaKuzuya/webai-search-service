#!/usr/bin/env python3
"""
Claude Session API - Maintains persistent Claude sessions with /clear support
"""

import os
import json
import subprocess
import uuid
import threading
import queue
import time
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import pty
import select
import fcntl
import termios
import struct

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Claude CLI path
CLAUDE_CLI = "/home/ubuntu/.npm-global/bin/claude"

# Global session storage
sessions = {}
session_lock = threading.Lock()

class ClaudeSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.master_fd, self.slave_fd = pty.openpty()
        self.process = None
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.reader_thread = None
        self.writer_thread = None
        self.is_running = False
        self.last_activity = time.time()
        self.creation_time = time.time()
        self.message_count = 0
        
    def start(self):
        """Start the Claude process"""
        try:
            # Set terminal size
            winsize = struct.pack('HHHH', 24, 80, 0, 0)
            fcntl.ioctl(self.slave_fd, termios.TIOCSWINSZ, winsize)
            
            # Start Claude in interactive mode
            self.process = subprocess.Popen(
                [CLAUDE_CLI],
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid,
                env=os.environ.copy()
            )
            
            os.close(self.slave_fd)
            self.slave_fd = None  # Mark as closed
            
            # Make master_fd non-blocking
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            self.is_running = True
            
            # Start reader thread
            self.reader_thread = threading.Thread(target=self._read_output)
            self.reader_thread.daemon = True
            self.reader_thread.start()
            
            # Start writer thread
            self.writer_thread = threading.Thread(target=self._write_input)
            self.writer_thread.daemon = True
            self.writer_thread.start()
            
            # Wait for initial prompt and clear initial output
            time.sleep(2)
            while not self.output_queue.empty():
                try:
                    self.output_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Check if process is still alive
            if self.process.poll() is not None:
                raise Exception(f"Claude process died immediately with code {self.process.returncode}")
            
            logger.info(f"Started Claude session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to start session {self.session_id}: {e}")
            self.stop()
            raise
    
    def _read_output(self):
        """Read output from Claude"""
        buffer = ""
        while self.is_running:
            try:
                # Check if data is available
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                if ready:
                    data = os.read(self.master_fd, 4096).decode('utf-8', errors='ignore')
                    if data:
                        buffer += data
                        # Send data immediately to queue for streaming
                        self.output_queue.put(data)
                        self.last_activity = time.time()
                    else:
                        # Empty read means EOF - process died
                        logger.warning(f"EOF on session {self.session_id} - process may have died")
                        self.is_running = False
                        break
            except OSError as e:
                logger.error(f"Read error on session {self.session_id}: {e}")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Unexpected read error on session {self.session_id}: {e}")
                self.is_running = False
                break
        
        # Send any remaining buffer
        if buffer:
            self.output_queue.put(buffer)
        
    def _write_input(self):
        """Write input to Claude"""
        while self.is_running:
            try:
                command = self.input_queue.get(timeout=0.1)
                if command:
                    os.write(self.master_fd, (command + '\n').encode('utf-8'))
                    self.last_activity = time.time()
            except queue.Empty:
                continue
            except OSError as e:
                logger.error(f"Write error on session {self.session_id}: {e}")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Unexpected write error on session {self.session_id}: {e}")
                self.is_running = False
                break
    
    def send_message(self, message):
        """Send a message to Claude"""
        self.input_queue.put(message)
        self.message_count += 1
        
    def is_healthy(self):
        """Check if session is healthy"""
        if not self.is_running:
            return False
        if self.process and self.process.poll() is not None:
            return False
        # Check if threads are alive
        if self.reader_thread and not self.reader_thread.is_alive():
            return False
        if self.writer_thread and not self.writer_thread.is_alive():
            return False
        return True
        
    def clear_context(self):
        """Send /clear command to Claude"""
        self.input_queue.put("/clear")
        # Wait for clear response
        try:
            self.get_response(timeout=5)
        except:
            pass  # Clear response not critical
        # Clear output queue
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
        self.last_activity = time.time()
                
    def get_response(self, timeout=60):
        """Get response from Claude"""
        response = ""
        start_time = time.time()
        last_chunk_time = time.time()
        
        logger.debug(f"Waiting for response from session {self.session_id}")
        
        while time.time() - start_time < timeout:
            try:
                chunk = self.output_queue.get(timeout=0.5)
                response += chunk
                last_chunk_time = time.time()
                logger.debug(f"Got chunk ({len(chunk)} chars): {repr(chunk[:50])}")
                
                # Look for Claude's prompt patterns
                # Claude CLI interactive mode shows "> " as prompt
                if response.rstrip().endswith('>'):
                    # Found prompt, extract actual response
                    lines = response.split('\n')
                    # Filter out prompts and echo of our command
                    result_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if stripped and not stripped.endswith('>') and not stripped.startswith('/'):
                            result_lines.append(line)
                    
                    result = '\n'.join(result_lines).strip()
                    logger.debug(f"Response complete: {len(result)} chars")
                    return result
                    
            except queue.Empty:
                # Check if session died
                if not self.is_running:
                    logger.warning(f"Session {self.session_id} is not running")
                    if response:
                        return response.strip()
                    raise Exception("Session terminated unexpectedly")
                
                # Check for inactivity timeout (no new data for 3 seconds)
                if response and (time.time() - last_chunk_time) > 3:
                    logger.debug(f"Inactivity timeout, returning {len(response)} chars")
                    return response.strip()
                continue
                
        # Timeout reached
        logger.warning(f"Response timeout after {timeout} seconds, got {len(response)} chars")
        if response:
            return response.strip()
        raise Exception(f"Response timeout after {timeout} seconds")
    
    def stop(self):
        """Stop the session"""
        self.is_running = False
        
        # Clean up process
        if self.process:
            try:
                self.process.terminate()
                # Give it time to terminate gracefully
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.process.kill()
                    self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping process for session {self.session_id}: {e}")
        
        # Clean up file descriptors
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass  # Already closed
            self.master_fd = None
            
        if self.slave_fd:
            try:
                os.close(self.slave_fd)
            except OSError:
                pass  # Already closed
            self.slave_fd = None
            
        logger.info(f"Stopped Claude session {self.session_id}")

def get_or_create_session(session_id=None):
    """Get existing session or create new one"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    with session_lock:
        # Check if we have an existing session
        if session_id in sessions:
            session = sessions[session_id]
            # Check if it's healthy
            if not session.is_healthy():
                logger.warning(f"Session {session_id} is unhealthy, recreating...")
                session.stop()
                del sessions[session_id]
                # Create new session
                session = ClaudeSession(session_id)
                session.start()
                sessions[session_id] = session
        else:
            # Create new session
            session = ClaudeSession(session_id)
            session.start()
            sessions[session_id] = session
        
        return sessions[session_id], session_id

def cleanup_old_sessions():
    """Clean up inactive sessions"""
    with session_lock:
        current_time = time.time()
        to_remove = []
        for sid, session in sessions.items():
            # Check if session is dead or inactive
            if not session.is_running or (current_time - session.last_activity > 1800):  # 30 minutes
                logger.info(f"Cleaning up session {sid} (running={session.is_running}, last_activity={current_time - session.last_activity:.1f}s ago)")
                session.stop()
                to_remove.append(sid)
        for sid in to_remove:
            del sessions[sid]

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    with session_lock:
        active_sessions = len(sessions)
        healthy_sessions = sum(1 for s in sessions.values() if s.is_healthy())
        session_details = []
        for sid, session in sessions.items():
            session_details.append({
                "id": sid,
                "healthy": session.is_healthy(),
                "running": session.is_running,
                "age": int(time.time() - session.creation_time),
                "last_activity": int(time.time() - session.last_activity),
                "message_count": session.message_count
            })
    
    return jsonify({
        "status": "healthy",
        "service": "claude-session-api",
        "active_sessions": active_sessions,
        "healthy_sessions": healthy_sessions,
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
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            session, _ = get_or_create_session(session_id)
            
            # Check session health before sending
            if not session.is_healthy():
                logger.warning(f"Session {session_id} unhealthy on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception("Session is unhealthy after retries")
            
            # Set model if needed (compare with default)
            if model != 'sonnet':  # Default is sonnet alias
                session.send_message(f"/model {model}")
                try:
                    session.get_response(timeout=5)
                except:
                    pass  # Model change response not critical
            
            # Send actual message
            session.send_message(message)
            response = session.get_response(timeout=300 if 'think' in message.lower() else 180)
            
            return jsonify({
                "session_id": session_id,
                "message": response
            })
            
        except Exception as e:
            logger.error(f"Error sending message (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                # On final attempt, try to clean up the session
                with session_lock:
                    if session_id in sessions:
                        sessions[session_id].stop()
                        del sessions[session_id]
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
            sessions[session_id].stop()
            del sessions[session_id]
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
    port = int(os.environ.get('PORT', 8002))
    logger.info(f"Starting Claude Session API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)