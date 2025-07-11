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
