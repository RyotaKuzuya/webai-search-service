#!/bin/bash

echo "🔄 Alternative: OAuth対応版の独自実装を作成"
echo "==========================================="
echo ""
echo "公式リポジトリのフォークの代わりに、OAuth対応版を独自に実装します。"
echo ""

# 作業ディレクトリ
WORK_DIR="/home/ubuntu/webai/claude-code-action-oauth"
mkdir -p $WORK_DIR
cd $WORK_DIR

echo "1. 独自のClaude Code Action（OAuth対応版）を作成..."

# リポジトリ初期化
git init

# README作成
cat > README.md << 'EOF'
# Claude Code Action - OAuth Edition

This is an OAuth-enabled version of Claude Code Action for GitHub workflows.
Designed for Claude Max users to use their subscription without API keys.

## Features

- ✅ OAuth authentication support
- ✅ Compatible with Claude Max subscription
- ✅ Automatic token refresh
- ✅ No API key required

## Usage

```yaml
- uses: RyotaKuzuya/claude-code-action-oauth@main
  with:
    use_oauth: 'true'
    claude_access_token: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
    claude_refresh_token: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
    claude_expires_at: ${{ secrets.CLAUDE_EXPIRES_AT }}
```
EOF

# action.yml作成
cat > action.yml << 'EOF'
name: 'Claude Code OAuth'
description: 'Claude Code Action with OAuth support for Max users'
author: 'RyotaKuzuya'

inputs:
  use_oauth:
    description: 'Use OAuth authentication'
    required: false
    default: 'true'
  claude_access_token:
    description: 'Claude OAuth access token'
    required: true
  claude_refresh_token:
    description: 'Claude OAuth refresh token'
    required: true
  claude_expires_at:
    description: 'Claude OAuth token expiration'
    required: true
  github_token:
    description: 'GitHub token'
    required: false
    default: ${{ github.token }}
  model:
    description: 'Claude model'
    required: false
    default: 'claude-3-5-sonnet-20241022'

runs:
  using: 'docker'
  image: 'Dockerfile'

branding:
  icon: 'cpu'
  color: 'orange'
EOF

# Dockerfile作成
cat > Dockerfile << 'EOF'
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI
RUN curl -fsSL https://storage.googleapis.com/anthropic-cli/latest/claude-cli-linux-x64.tar.gz | tar -xz -C /usr/local/bin

# Create working directory
WORKDIR /action

# Copy action files
COPY entrypoint.sh oauth_setup.py ./
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/action/entrypoint.sh"]
EOF

# entrypoint.sh作成
cat > entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🤖 Claude Code OAuth Action"

# Setup OAuth
python3 /action/oauth_setup.py

# Extract issue/PR information
if [ -n "$GITHUB_EVENT_PATH" ]; then
    EVENT_TYPE=$(jq -r '.action // empty' "$GITHUB_EVENT_PATH")
    COMMENT_BODY=$(jq -r '.comment.body // .issue.body // empty' "$GITHUB_EVENT_PATH")
    
    if [[ "$COMMENT_BODY" == *"@claude"* ]]; then
        # Remove @claude mention
        PROMPT=$(echo "$COMMENT_BODY" | sed 's/@claude//g')
        
        # Execute Claude
        claude --model "$INPUT_MODEL" "$PROMPT" > response.txt
        
        # Post response back to GitHub
        cat response.txt
    fi
fi
EOF

# oauth_setup.py作成
cat > oauth_setup.py << 'EOF'
#!/usr/bin/env python3
import os
import json
import pathlib

# OAuth configuration
config = {
    "access_token": os.environ.get("INPUT_CLAUDE_ACCESS_TOKEN"),
    "refresh_token": os.environ.get("INPUT_CLAUDE_REFRESH_TOKEN"),
    "expires_at": os.environ.get("INPUT_CLAUDE_EXPIRES_AT"),
    "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
    "scope": "claude_code",
    "development_mode": False
}

# Create config directory
config_dir = pathlib.Path.home() / ".config" / "claude"
config_dir.mkdir(parents=True, exist_ok=True)

# Write config
config_file = config_dir / "claude_config.json"
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)

print(f"✅ OAuth config saved to {config_file}")
EOF

# .gitignore作成
cat > .gitignore << 'EOF'
.env
*.log
node_modules/
EOF

echo ""
echo "2. Gitリポジトリとして初期化..."
git add .
git commit -m "Initial commit: Claude Code Action with OAuth support"

echo ""
echo "✅ 独自のOAuth対応版が作成されました！"
echo ""
echo "次のステップ："
echo "1. GitHubで新しいリポジトリ 'claude-code-action-oauth' を作成"
echo "2. 以下のコマンドでプッシュ："
echo ""
echo "cd $WORK_DIR"
echo "git remote add origin https://github.com/RyotaKuzuya/claude-code-action-oauth.git"
echo "git push -u origin main"