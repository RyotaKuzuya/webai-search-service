FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install Python dependencies
RUN pip install flask flask-cors requests gunicorn

# Create directories for config and logs
RUN mkdir -p /root/.claude /app/logs /claude-home /usr/local/bin

# Copy all server files
COPY api_server.py api_server_production.py claude_integration.py simple_claude_bridge.py gunicorn_config.py start_production.sh claude_wrapper.sh /app/
RUN chmod +x /app/start_production.sh /app/claude_wrapper.sh

# Create a symlink for claude command
RUN ln -s /app/claude_wrapper.sh /usr/local/bin/claude

# Expose port
EXPOSE 8000

# Run the API server
CMD ["/app/start_production.sh"]