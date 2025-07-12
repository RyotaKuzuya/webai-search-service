# Claude Max Plan OAuth セットアップガイド

## 概要

Claude Max PlanでGitHub Actionsを無料で使用するためのOAuth認証設定手順です。

## 前提条件

- Claude Max Planに加入していること
- GitHub リポジトリの管理者権限があること

## セットアップ手順

### 1. Claude CLIでOAuthトークンを生成

```bash
# セットアップスクリプトを実行
./generate_claude_oauth_token.sh

# または手動で実行
claude auth
```

### 2. GitHub Secretsに追加

1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions** に移動
2. **New repository secret** をクリック
3. 以下の情報を入力:
   - **Name**: `CLAUDE_CODE_OAUTH_TOKEN`
   - **Value**: 生成されたOAuthトークン

### 3. ワークフローの確認

`.github/workflows/claude-code-actions.yml` が以下のように設定されていることを確認:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

## トークンの取得方法

### 方法1: Claude CLIから直接取得

```bash
# 認証情報ファイルの場所
cat ~/.config/claude/claude_config.json
```

### 方法2: Claude Codeから取得

```bash
# Claude Codeを起動
claude

# 以下のコマンドを実行
cat ~/.config/claude/claude_config.json | jq -r '.oauth_token'
```

## トラブルシューティング

### エラー: "Authentication failed"

1. Claude Max Planに加入しているか確認
2. `claude auth` で再認証

### エラー: "Token expired"

```bash
# トークンを再生成
claude auth --refresh
```

### ワークフローが失敗する場合

1. GitHub Secretsが正しく設定されているか確認
2. Secret名が `CLAUDE_CODE_OAUTH_TOKEN` になっているか確認
3. ワークフローファイルで `claude_code_oauth_token` を使用しているか確認

## 注意事項

- OAuthトークンは安全に管理してください
- トークンをコードに直接記述しないでください
- 定期的にトークンを更新することを推奨します

## 参考リンク

- [Claude Code Actions 公式ドキュメント](https://github.com/anthropics/claude-code-action)
- [Claude Max Plan](https://claude.ai/pricing)