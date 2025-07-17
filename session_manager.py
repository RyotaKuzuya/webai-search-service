#!/usr/bin/env python3
"""
Session and Chat History Manager for WebAI
"""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
import os

class SessionManager:
    def __init__(self, db_path='webai.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create chats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            ''')
            
            # Create sessions table for persistent context
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def create_chat(self, user_id, title=None):
        """Create a new chat session"""
        if not title:
            title = f"チャット {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO chats (user_id, title) VALUES (?, ?)',
                (user_id, title)
            )
            chat_id = cursor.lastrowid
            conn.commit()
            
        return chat_id
    
    def get_user_chats(self, user_id, limit=50):
        """Get user's chat list"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, created_at, updated_at
                FROM chats
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            chats = []
            for row in cursor.fetchall():
                chats.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                })
            
            return chats
    
    def get_chat_messages(self, chat_id):
        """Get messages for a specific chat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, role, content, created_at
                FROM messages
                WHERE chat_id = ?
                ORDER BY created_at ASC
            ''', (chat_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'role': row[1],
                    'content': row[2],
                    'created_at': row[3]
                })
            
            return messages
    
    def add_message(self, chat_id, role, content):
        """Add a message to a chat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
                (chat_id, role, content)
            )
            
            # Update chat's updated_at timestamp
            cursor.execute(
                'UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (chat_id,)
            )
            
            # Update chat title if it's the first user message
            if role == 'user':
                cursor.execute(
                    'SELECT COUNT(*) FROM messages WHERE chat_id = ? AND role = "user"',
                    (chat_id,)
                )
                count = cursor.fetchone()[0]
                if count == 1:  # First user message
                    # Use first 50 characters of message as title
                    title = content[:50] + ('...' if len(content) > 50 else '')
                    cursor.execute(
                        'UPDATE chats SET title = ? WHERE id = ?',
                        (title, chat_id)
                    )
            
            conn.commit()
    
    def delete_chat(self, chat_id):
        """Delete a chat and all its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
            conn.commit()
    
    def get_session_context(self, user_id):
        """Get saved session context for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT context FROM sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
                (user_id,)
            )
            row = cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            return None
    
    def save_session_context(self, user_id, context):
        """Save session context for a user"""
        session_id = str(uuid.uuid4())
        context_json = json.dumps(context)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (id, user_id, context, updated_at)
                VALUES (
                    COALESCE((SELECT id FROM sessions WHERE user_id = ? LIMIT 1), ?),
                    ?,
                    ?,
                    CURRENT_TIMESTAMP
                )
            ''', (user_id, session_id, user_id, context_json))
            conn.commit()
    
    def clear_session_context(self, user_id):
        """Clear session context for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            conn.commit()
    
    def build_conversation_history(self, chat_id, limit=20):
        """Build conversation history for Claude API"""
        messages = self.get_chat_messages(chat_id)
        
        # Limit to recent messages to avoid token limits
        if len(messages) > limit:
            messages = messages[-limit:]
        
        # Format for Claude API
        conversation = []
        for msg in messages:
            conversation.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        return conversation