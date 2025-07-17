#!/usr/bin/env python3
"""Test file upload functionality"""

import requests
import os

# Create a test file
test_content = """これはテストファイルです。
日本語も含まれています。
ファイルアップロード機能のテストです。"""

with open('test_upload.txt', 'w', encoding='utf-8') as f:
    f.write(test_content)

# Login first
login_url = 'http://localhost:5000/api/login'
login_data = {'username': 'kuzuya', 'password': 'kuzuya00'}

session = requests.Session()
login_response = session.post(login_url, json=login_data)
print(f"Login status: {login_response.status_code}")

# Test file upload
upload_url = 'http://localhost:5000/api/upload'
with open('test_upload.txt', 'rb') as f:
    files = {'file': ('test_upload.txt', f, 'text/plain')}
    response = session.post(upload_url, files=files)

print(f"Upload status: {response.status_code}")
print(f"Response: {response.text}")

# Clean up
os.remove('test_upload.txt')