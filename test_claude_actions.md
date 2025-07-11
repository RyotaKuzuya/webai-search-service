# Claude GitHub Actions テスト手順

## 1. Issueでのテスト

GitHubで以下の手順を実行してください：

1. https://github.com/RyotaKuzuya/webai-search-service/issues にアクセス
2. "New issue" をクリック
3. 以下の内容でIssueを作成：

**Title:**
```
🧪 Claude Code Actions テスト
```

**Body:**
```
@claude WebAIプロジェクトの簡単なコードレビューをしてください。特にsimple_api.pyの品質を確認してください。
```

## 2. Pull Requestでのテスト

1. 小さな変更を含むブランチを作成：

```bash
cd /home/ubuntu/webai
git checkout -b test-claude-actions
echo "# Claude Actions Test" >> test_file.md
git add test_file.md
git commit -m "Test: Claude Actions PR review"
git push origin test-claude-actions
```

2. GitHubでPRを作成
3. PRが作成されると自動的にClaude Codeが実行されます

## 3. 手動実行でのテスト

1. https://github.com/RyotaKuzuya/webai-search-service/actions にアクセス
2. "Claude Code Official" ワークフローを選択
3. "Run workflow" をクリック
4. プロンプトに以下を入力：

```
WebAIプロジェクトのセキュリティ監査を実行してください。SQLインジェクション、XSS、認証の問題を重点的に確認してください。
```

## 期待される結果

- Issue/PRにClaude Codeからのコメントが追加される
- コードレビューや改善提案が表示される
- エラーが発生した場合は、OAuth Tokenの設定を確認

## トラブルシューティング

### "Bad credentials" エラー
→ OAuth Tokenが正しく設定されていません
```bash
./setup_claude_oauth_token.sh
```

### ワークフローが実行されない
→ ワークフローの権限を確認
- Settings → Actions → General → Workflow permissions
- "Read and write permissions" を選択

### Claude Codeが応答しない
→ Claude Maxアカウントの状態を確認
```bash
claude /status
```