# 🚀 簡単プッシュガイド

## 方法1: スクリプトを使用（推奨）

```bash
./setup_github_token.sh
```

スクリプトが手順を案内します。

## 方法2: 手動でコマンド実行

1. **GitHubでトークン作成**
   - https://github.com/settings/tokens/new
   - Scopes: ☑ repo
   - Generate token

2. **以下のコマンドを実行**（YOUR_TOKENを置き換え）
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/RyotaKuzuya/webai-search-service.git
   git push origin master
   git remote set-url origin https://github.com/RyotaKuzuya/webai-search-service.git
   ```

## プッシュ後のテスト

1. **新しいIssue作成**
   https://github.com/RyotaKuzuya/webai-search-service/issues/new

2. **コメントでテスト**
   ```
   @claude
   Max Plan動作テストです。
   ```

3. **確認**
   - Actions: https://github.com/RyotaKuzuya/webai-search-service/actions
   - startup_failureではなく正常実行されるはず

## 🎯 期待される結果

- ✅ GitHub Actions無料実行（Publicリポジトリ）
- ✅ Claude応答（Max Plan認証）
- ✅ エラーなし

これで完全無料のClaude AI + GitHub Actionsが実現します！