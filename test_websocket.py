#!/usr/bin/env python3
import socketio
import json
import time

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to WebSocket')

@sio.event
def disconnect():
    print('Disconnected from WebSocket')

@sio.event
def connected(data):
    print(f'Server message: {data}')

@sio.event
def message_received(data):
    print(f'Message received: {data}')

@sio.event
def stream_chunk(data):
    print(f'Stream chunk: {data["chunk"]}', end='', flush=True)

@sio.event
def stream_complete(data):
    print(f'\nStream complete: {data}')

@sio.event
def error(data):
    print(f'Error: {data}')

# Connect to the server
try:
    print('Connecting to https://your-domain.com...')
    sio.connect('https://your-domain.com', 
                transports=['websocket'],
                headers={'Cookie': 'session=test'})
    
    # Send a test message
    print('Sending test message...')
    sio.emit('message', {
        'message': 'Hello, Claude!',
        'model': 'claude-opus-4-20250514',
        'web_search': False
    })
    
    # Wait for response
    time.sleep(10)
    
    # Disconnect
    sio.disconnect()
    
except Exception as e:
    print(f'Connection error: {e}')