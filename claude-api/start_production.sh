#!/bin/bash

# Production startup script for Claude API

# Create logs directory
mkdir -p /app/logs

# Check if we should use production server
if [ "$PRODUCTION" = "true" ]; then
    echo "Starting Claude API in production mode..."
    exec gunicorn -c gunicorn_config.py api_server_production:app
else
    echo "Starting Claude API in development mode..."
    exec python api_server.py
fi