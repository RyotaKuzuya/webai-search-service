# 🎉 トークン設定完了！

## すぐにテストする

### 方法1: 新しいIssueでテスト
👉 **[ここをクリックして新しいIssue作成](https://github.com/RyotaKuzuya/webai-search-service/issues/new)**

**Issue内容:**
- タイトル: `OAuth Token Test`
- 本文: `Testing Claude Max Plan OAuth`

投稿後、コメントに:
```
@claude
Hello! Testing new OAuth token.
```

### 方法2: 既存のIssueでテスト
既存のIssueのコメントに `@claude` を追加するだけでもOK！

## 確認方法

### ワークフロー実行状況
👉 **[GitHub Actions](https://github.com/RyotaKuzuya/webai-search-service/actions)**

### 期待される結果
- ✅ Claude Code Actionが起動
- ✅ Claudeがコメントに返信
- ✅ ワークフローが成功

## トラブルシューティング

もし失敗した場合:
1. Actionsタブでエラーログを確認
2. `startup_failure` の場合はトークンの形式を確認
3. 権限エラーの場合はClaude GitHub Appのインストール状況を確認