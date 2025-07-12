# Claude Max OAuth GitHub Actions セットアップ手順

## 1. GitHubシークレットの設定

以下の3つのシークレットをGitHubリポジトリに設定してください：

### シークレット設定ページ
https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions

### 設定するシークレット

1. **CLAUDE_ACCESS_TOKEN**
   ```
   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
   ```

2. **CLAUDE_REFRESH_TOKEN**
   ```
   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
   ```

3. **CLAUDE_EXPIRES_AT**
   ```
   2025-07-08T00:00:00Z
   ```

## 2. 必要なリポジトリのフォーク

以下のリポジトリをフォークしてください：

1. https://github.com/anthropics/claude-code-action
2. https://github.com/anthropics/claude-code-base-action

## 3. ワークフローファイルの更新

`.github/workflows/claude-oauth.yml` の以下の行を更新：

```yaml
uses: your-username/claude-code-action@main
```

を

```yaml
uses: RyotaKuzuya/claude-code-action@main
```

に変更（フォーク後）

## 4. テスト

1. 新しいIssueを作成
2. `@claude テストメッセージ` とコメント
3. GitHub Actionsが起動することを確認

## 注意事項

- トークンの有効期限は 2025-07-08 です
- 期限が近づいたら `refresh_claude_oauth_tokens.py` を実行して更新してください
- APIキー（ANTHROPIC_API_KEY）は削除してOKです