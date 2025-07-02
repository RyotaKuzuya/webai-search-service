#!/usr/bin/env python3
import time
import sys

print("Testing WebSocket connection...")

# First, login to get session
import requests

login_url = "https://your-domain.com/api/login"
login_data = {"username": "admin", "password": "WebAI@2024SecurePass!"}

session = requests.Session()
session.verify = False  # Ignore SSL for testing

print("1. Logging in...")
response = session.post(login_url, json=login_data)
print(f"Login response: {response.status_code}")
if response.status_code != 200:
    print(f"Login failed: {response.text}")
    sys.exit(1)

# Get session cookie
cookies = session.cookies.get_dict()
print(f"Cookies: {cookies}")

# Now test WebSocket with session
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to WebSocket!')

@sio.event
def disconnect():
    print('Disconnected from WebSocket')

@sio.event
def message_received(data):
    print(f'Message received acknowledgment: {data}')

@sio.event
def stream_chunk(data):
    print(f'Chunk: {data.get("chunk", "")}', end='', flush=True)

@sio.event
def stream_complete(data):
    print(f'\nStream complete: {data}')

@sio.event
def error(data):
    print(f'Error: {data}')

try:
    print("\n2. Connecting WebSocket...")
    # Convert cookies to header format
    cookie_header = '; '.join([f'{k}={v}' for k, v in cookies.items()])
    
    sio.connect('https://your-domain.com', 
                transports=['websocket'],
                headers={'Cookie': cookie_header},
                wait_timeout=10)
    
    print("3. Sending test message...")
    sio.emit('message', {
        'message': 'Hello, this is a test',
        'model': 'claude-opus-4-20250514',
        'web_search': False
    })
    
    # Wait for response
    print("4. Waiting for response...")
    time.sleep(15)
    
    print("5. Disconnecting...")
    sio.disconnect()
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()