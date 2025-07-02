#!/bin/bash
# Wrapper script to use host's claude command from within container

# Use the mounted claude credentials
export HOME=/root
export CLAUDE_HOME=/claude-home

# Copy credentials to expected location
if [ -f "/claude-home/.credentials.json" ]; then
    mkdir -p ~/.claude
    cp /claude-home/.credentials.json ~/.claude/
    chmod 600 ~/.claude/.credentials.json
fi

# Execute the claude command with arguments
exec /usr/local/bin/claude "$@"