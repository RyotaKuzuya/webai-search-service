# Claude Code OAuth認証ガイド

## なぜURLが繋がらないのか

提供したURL `https://auth.claude.ai/oauth/authorize?...` は、Claude Code CLIの内部処理用で、ブラウザから直接アクセスすることはできません。

## 正しい認証手順

### 手順1: Claude CLIで認証開始

```bash
claude auth
```

### 手順2: 正しいURLが表示される

CLIが自動的に正しい認証URLを生成し表示します。このURLは：
- `https://claude.ai/...` で始まります（auth.claude.ai ではない）
- ブラウザで開くことができます

### 手順3: ブラウザで認証

1. Anthropicアカウントでログイン
2. 認証を承認
3. 認証コードが表示される

### 手順4: 認証コード入力

ターミナルに戻って認証コードを貼り付け

### 手順5: トークン確認

```bash
cat ~/.config/claude/claude_config.json | jq -r '.oauth_token'
```

## GitHub Actionsへの設定

取得したトークンを GitHub Secrets の `CLAUDE_CODE_OAUTH_TOKEN` に設定してください。

## トラブルシューティング

- Claude CLIがない場合: `curl -fsSL https://cli.claude.ai/install.sh | sh`
- 認証が失敗する場合: `claude setup-token` を試す
- トークンが見つからない場合: `~/.config/claude/` ディレクトリを確認