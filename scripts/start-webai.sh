#!/bin/bash

# WebAI Service Startup Script

set -e

echo "=== WebAI Service 起動スクリプト ==="
echo

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Dockerコンテナ内で実行中..."
    # In Docker, use gunicorn
    exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
else
    echo "ローカル環境で実行中..."
    
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        echo "仮想環境を作成中..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "依存関係をインストール中..."
    pip install -r requirements.txt
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Start the application
    echo "アプリケーションを起動中..."
    python app.py
fi