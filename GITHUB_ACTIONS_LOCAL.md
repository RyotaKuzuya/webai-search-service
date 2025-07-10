# 🚀 GitHub Actions ローカル実行ガイド

## 概要
GitHub Actionsの課金制限を回避し、Claude Codeをローカルで実行する方法です。

## なぜローカル実行が必要か

1. **GitHub課金制限**: プライベートリポジトリでのActions実行は有料
2. **Claude Max認証**: GitHub Actions環境でClaude CLIの直接実行は困難
3. **柔軟性**: ローカル環境の方が柔軟な実行が可能

## 実行方法

### 方法1: インタラクティブスクリプト（推奨）
```bash
cd /home/ubuntu/webai
./claude_local_executor.sh
```

メニューから選択：
- 📝 コードレビュー
- 🐛 バグ修正
- ⚡ パフォーマンス最適化
- 🔒 セキュリティチェック
- 📦 依存関係の更新
- 🎯 カスタムタスク

### 方法2: 直接Claude CLI実行
```bash
cd /home/ubuntu/webai

# コードレビュー
claude "WebAIプロジェクトのコードレビューをしてください" --model sonnet4

# バグ修正
claude "simple_api.pyの無言応答問題を修正してください" --model opus4 --thinking

# パフォーマンス最適化
claude "megathink: WebAIのレスポンス時間を改善してください" --model sonnet4
```

### 方法3: 既存のバイパススクリプト
```bash
./github_actions_bypass.sh
```

## GitHub Actionsワークフロー

### claude-local-runner.yml
手動トリガーでタスクを記録し、ローカル実行を促すワークフローです。

実行方法：
1. GitHub → Actions → Claude Local Runner
2. "Run workflow"をクリック
3. タスクタイプとモデルを選択
4. 実行後、Issueが作成される
5. Issueの指示に従ってローカルで実行

## タスクタイプ

### 1. コードレビュー
- セキュリティの問題チェック
- パフォーマンスの改善点
- コード品質の確認
- ベストプラクティスの遵守

### 2. バグ修正
- 既知のバグの調査と修正
- エラーログの確認
- 潜在的な問題の特定

### 3. パフォーマンス最適化
- レスポンス時間の改善
- リソース使用量の削減
- 並行処理の最適化

### 4. セキュリティチェック
- SQLインジェクション対策
- XSS対策
- 認証・認可の確認
- セキュアな設定の確認

### 5. 依存関係の更新
- requirements.txtの確認
- セキュリティアップデート
- 互換性の確認

## ベストプラクティス

### 定期実行
```bash
# cronで週次実行を設定
crontab -e

# 毎週日曜日の午前3時に実行
0 3 * * 0 cd /home/ubuntu/webai && ./claude_local_executor.sh
```

### 実行ログの管理
```bash
# ログディレクトリ作成
mkdir -p /home/ubuntu/webai/claude_results

# ログの確認
ls -la claude_results/

# 最新のログを表示
cat claude_results/task_*.log | tail -n 50
```

### Git操作との連携
```bash
# 変更前にブランチ作成
git checkout -b claude-improvements

# Claude実行
./claude_local_executor.sh

# 変更をコミット
git add -A
git commit -m "🤖 Claude による改善"
git push origin claude-improvements
```

## トラブルシューティング

### Claude CLIが見つからない
```bash
# Claude CLIの確認
which claude

# 再インストール
claude --version
```

### 認証エラー
```bash
# 認証状態確認
claude /status

# 再ログイン
claude
```

### タイムアウト
思考モードの選択を調整：
- 通常: 短いタスク
- think: 中規模タスク
- megathink: 大規模タスク
- think harder: 複雑なタスク

## セキュリティ注意事項

1. **認証情報の保護**
   - Claude認証情報を共有しない
   - ~/.claude/ディレクトリの権限を確認

2. **実行結果の確認**
   - 自動生成されたコードは必ずレビュー
   - テスト環境で確認後に本番適用

3. **ログの管理**
   - 機密情報を含むログは適切に管理
   - 定期的な古いログの削除

## まとめ

GitHub Actionsの課金制限を回避しつつ、Claude Codeの強力な機能を活用できます。ローカル実行により：

✅ 無料で実行可能
✅ 柔軟な制御
✅ 即座のフィードバック
✅ 完全な環境アクセス

定期的にclaude_local_executor.shを実行して、プロジェクトの品質を維持しましょう！