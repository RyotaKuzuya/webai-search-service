#!/bin/bash
# Claude CLI wrapper script
# This ensures the environment is properly set up

export HOME=/home/ubuntu
export PATH="/home/ubuntu/.npm-global/bin:$PATH"
export NODE_PATH="/home/ubuntu/.npm-global/lib/node_modules"

# Change to claude-code directory where yoga.wasm exists
cd /home/ubuntu/.npm-global/lib/node_modules/@anthropic-ai/claude-code

# Execute claude with all arguments
exec node /home/ubuntu/.npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js "$@"