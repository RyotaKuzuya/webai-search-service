# 🚀 Claude Max + GitHub Actions セットアップガイド

## 概要
Claude MaxプランでGitHub Actionsを使い放題にする設定方法です。
これにより、追加料金なしでClaude Code Assistantを活用できます！

## 前提条件
- ✅ Claude Maxプランに加入済み
- ✅ Claude Codeにログイン済み
- ✅ GitHubリポジトリの管理者権限

## セットアップ手順

### 1. Claude認証情報の確認

```bash
# Claude Codeの状態確認
claude
/status

# Login Method: Claude Max Account と表示されることを確認
```

### 2. GitHub Appのインストール

```bash
# Claude Code内で実行
/install-github-app
```

### 3. 認証トークンの取得

認証情報は以下のファイルに保存されています：
```bash
# Linux/Ubuntu
cat ~/.claude/.credentials.json

# macOS
# Keychainで "Claude" を検索

# Windows
# %APPDATA%\claude\.credentials.json
```

### 4. GitHub Secretsの設定

GitHubリポジトリで以下を設定：
1. Settings → Secrets and variables → Actions
2. New repository secret

追加する3つのシークレット：
- `CLAUDE_ACCESS_TOKEN`: accessTokenの値
- `CLAUDE_REFRESH_TOKEN`: refreshTokenの値
- `CLAUDE_EXPIRES_AT`: expiresAtの値

⚠️ **重要**: これらのトークンは絶対に公開しないでください！

### 5. ワークフローの有効化

```bash
# リポジトリにプッシュ
git add .github/workflows/
git commit -m "🚀 Claude Max GitHub Actions設定を追加"
git push
```

## 使い方

### PRレビュー
PRを作成すると自動的にClaudeがレビューします。

### 手動実行
1. GitHub → Actions → Claude Code Assistant
2. Run workflow
3. プロンプトを入力して実行

### Issue内でのコメント
```
@claude このバグを修正してください
```

### 定期メンテナンス
毎週日曜日に自動実行されます。

## トラブルシューティング

### エラー: "Authentication failed"
→ トークンの有効期限切れ。Claude Codeで再ログイン後、Secretsを更新。

### エラー: "Rate limit exceeded"
→ Claude Maxの制限に達した。時間をおいて再実行。

### エラー: "Workflow not triggered"
→ ワークフローの権限設定を確認。

## セキュリティのベストプラクティス

1. **トークンの定期更新**
   - 月1回程度、認証情報を更新
   
2. **最小権限の原則**
   - 必要なリポジトリのみにアクセス許可

3. **監査ログの確認**
   - Settings → Audit log で不審なアクティビティをチェック

## 注意事項

⚠️ これは非公式な使用方法です。以下に注意：
- Anthropic社のサポート対象外
- 利用規約の変更により使用できなくなる可能性
- 複数リポジトリでの共有は避ける

## 参考リンク

- [Notion - 詳細ガイド](https://tourmaline-skateboard-bbd.notion.site/Claude-Max-GitHub-Actions-200f07a4546480e798f1fab2e36259b7)
- [Guillaume Raille - オリジナル記事](https://grll.bearblog.dev/use-claude-github-actions-with-claude-max/)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- [grll/claude-code-base-action](https://github.com/grll/claude-code-base-action)

---

🎉 **おめでとうございます！** 
Claude MaxプランでGitHub Actionsが使い放題になりました！