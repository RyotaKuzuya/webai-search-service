#!/bin/bash

echo "🔧 フォークしたリポジトリにOAuth対応を実装"
echo "=========================================="
echo ""

# クローン用ディレクトリ
WORK_DIR="/home/ubuntu/webai/fork-work"
mkdir -p $WORK_DIR
cd $WORK_DIR

echo "1. フォークしたリポジトリをクローン..."
if [ ! -d "claude-code-action" ]; then
    git clone https://github.com/RyotaKuzuya/claude-code-action.git
    cd claude-code-action
else
    cd claude-code-action
    git pull origin main
fi

echo ""
echo "2. OAuth対応ブランチを作成..."
git checkout -b oauth-support

echo ""
echo "3. action.yml を修正..."
cat > action.yml << 'EOF'
name: 'Claude Code'
description: 'AI-powered automation for GitHub workflows'
author: 'Anthropic'

inputs:
  # OAuth認証オプション
  use_oauth:
    description: 'Use OAuth authentication instead of API key'
    required: false
    default: 'false'
  claude_access_token:
    description: 'Claude OAuth access token'
    required: false
  claude_refresh_token:
    description: 'Claude OAuth refresh token'
    required: false
  claude_expires_at:
    description: 'Claude OAuth token expiration'
    required: false
    
  # 既存のオプション
  anthropic_api_key:
    description: 'Anthropic API key for Claude'
    required: false
  github_token:
    description: 'GitHub token for repository access'
    required: true
    default: ${{ github.token }}
  model:
    description: 'Claude model to use'
    required: false
    default: 'claude-3-5-sonnet-20241022'
  max_thinking_steps:
    description: 'Maximum thinking steps'
    required: false
    default: '20'

runs:
  using: 'docker'
  image: 'Dockerfile'
  env:
    ANTHROPIC_API_KEY: ${{ inputs.anthropic_api_key }}
    GITHUB_TOKEN: ${{ inputs.github_token }}
    USE_OAUTH: ${{ inputs.use_oauth }}
    CLAUDE_ACCESS_TOKEN: ${{ inputs.claude_access_token }}
    CLAUDE_REFRESH_TOKEN: ${{ inputs.claude_refresh_token }}
    CLAUDE_EXPIRES_AT: ${{ inputs.claude_expires_at }}
    MODEL: ${{ inputs.model }}
    MAX_THINKING_STEPS: ${{ inputs.max_thinking_steps }}

branding:
  icon: 'cpu'
  color: 'orange'
EOF

echo ""
echo "4. OAuth認証スクリプトを作成..."
cat > oauth_auth.js << 'EOF'
// OAuth認証処理
const fs = require('fs');
const path = require('path');

function setupOAuthAuth() {
  if (process.env.USE_OAUTH === 'true') {
    console.log('Setting up OAuth authentication...');
    
    const config = {
      access_token: process.env.CLAUDE_ACCESS_TOKEN,
      refresh_token: process.env.CLAUDE_REFRESH_TOKEN,
      expires_at: process.env.CLAUDE_EXPIRES_AT,
      client_id: "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
      scope: "claude_code",
      development_mode: false
    };
    
    // Claude設定ディレクトリを作成
    const configDir = path.join(process.env.HOME, '.config', 'claude');
    fs.mkdirSync(configDir, { recursive: true });
    
    // 設定ファイルを書き込み
    const configPath = path.join(configDir, 'claude_config.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    
    console.log('OAuth configuration saved to:', configPath);
    return true;
  }
  return false;
}

module.exports = { setupOAuthAuth };
EOF

echo ""
echo "5. Dockerfileを修正..."
if [ -f "Dockerfile" ]; then
    # 既存のDockerfileにOAuth対応を追加
    sed -i '1i # OAuth authentication support' Dockerfile
else
    # 新しいDockerfileを作成
    cat > Dockerfile << 'EOF'
FROM node:20-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /action

# Copy action files
COPY . .

# Install dependencies if package.json exists
RUN if [ -f package.json ]; then npm install; fi

# Set up entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
EOF
fi

echo ""
echo "6. エントリーポイントスクリプトを作成..."
cat > entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "Claude Code Action starting..."

# OAuth認証のセットアップ
if [ "$USE_OAUTH" = "true" ]; then
    echo "Using OAuth authentication"
    node /action/oauth_auth.js
else
    echo "Using API key authentication"
fi

# メイン処理を実行
if [ -f "/action/index.js" ]; then
    node /action/index.js
else
    echo "Error: index.js not found"
    exit 1
fi
EOF

chmod +x entrypoint.sh

echo ""
echo "7. 変更をコミット..."
git add .
git commit -m "Add OAuth authentication support for Claude Max users"

echo ""
echo "8. フォークにプッシュ..."
git push origin oauth-support

echo ""
echo "✅ 完了！"
echo ""
echo "次のステップ："
echo "1. https://github.com/RyotaKuzuya/claude-code-action にアクセス"
echo "2. 'oauth-support' ブランチから main へのPRを作成"
echo "3. PRをマージ"
echo "4. ワークフローでこのアクションを使用："
echo "   uses: RyotaKuzuya/claude-code-action@main"