#!/bin/bash

echo "🚀 公式リポジトリのフォーク手順"
echo "================================"
echo ""
echo "以下の手順でフォークを実行してください："
echo ""
echo "1. claude-code-action のフォーク："
echo "   https://github.com/anthropics/claude-code-action"
echo "   → 右上の「Fork」ボタンをクリック"
echo "   → Create fork をクリック"
echo ""
echo "2. フォークが完了したら、OAuth対応のコードを追加します"
echo ""

# フォーク後に追加するOAuth対応コード
cat > /home/ubuntu/webai/oauth_modifications.md << 'EOF'
# OAuth対応の修正内容

## 1. action.yml の修正

```yaml
inputs:
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
```

## 2. index.js の修正（メイン処理）

```javascript
// OAuth認証の処理を追加
if (core.getInput('use_oauth') === 'true') {
  const accessToken = core.getInput('claude_access_token');
  const refreshToken = core.getInput('claude_refresh_token');
  const expiresAt = core.getInput('claude_expires_at');
  
  // OAuth認証の設定
  process.env.CLAUDE_ACCESS_TOKEN = accessToken;
  process.env.CLAUDE_REFRESH_TOKEN = refreshToken;
  process.env.CLAUDE_EXPIRES_AT = expiresAt;
}
```
EOF

echo "3. フォーク完了後、以下のコマンドを実行："
echo "   ./implement_oauth_in_fork.sh"