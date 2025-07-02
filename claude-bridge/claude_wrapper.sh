#!/bin/bash
# Wrapper script to properly execute claude

cd /home/ubuntu/.npm-global/lib/node_modules/@anthropic-ai/claude-code
exec /home/ubuntu/.npm-global/bin/claude "$@"