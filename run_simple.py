#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, socketio

if __name__ == '__main__':
    print("\n" + "="*50)
    print("WebAI Local Test Server")
    print("="*50)
    print("\nAccess the application at: http://localhost:5000")
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
