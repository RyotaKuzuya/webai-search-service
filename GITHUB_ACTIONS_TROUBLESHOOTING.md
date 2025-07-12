# GitHub Actions トラブルシューティング完全ガイド

## 🔍 発見された問題と解決策

### 1. **anthropics/claude-code-action は実在する** ✅
- 公式リポジトリ: https://github.com/anthropics/claude-code-action
- GitHub Marketplace に掲載済み
- バージョン: `@v1` を使用すべき（`@main`ではなく）

### 2. **OAuth認証の問題**
claude-code-action は以下の認証方法をサポート：
- `anthropic-api-key` - 通常のAPIキー
- `claude_code_oauth_token` - Claude Max/Pro用OAuthトークン

**現在の設定は `claude_code_oauth_token` だが、正しいパラメータ名は不明**

### 3. **GitHub Actions実行の確認方法**

#### A. Actions タブで確認
1. https://github.com/RyotaKuzuya/webai-search-service/actions
2. ワークフローが表示されない場合：
   - リポジトリ設定でActionsが有効か確認
   - ワークフローファイルが正しいブランチにあるか確認

#### B. 実行されない理由の可能性
1. **課金制限** - Private リポジトリの無料枠超過
2. **権限設定** - Repository settings → Actions → General
3. **ワークフロー無効化** - 個別のワークフローが無効になっている

### 4. **即座のテスト方法**

#### ステップ1: シンプルなワークフローでテスト
```yaml
name: Simple Echo Test
on:
  push:
    branches: [master]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "GitHub Actions is working!"
```

#### ステップ2: Issue コメントトリガーのテスト
Issue #3 または新しいIssueで：
- `@test` - debug-test.yml をトリガー
- `@claude` - claude-api-direct.yml をトリガー

### 5. **修正済みの問題**
- ✅ debug-test.yml に permissions を追加
- ✅ claude-code-actions.yml を @v1 に変更
- ✅ ワークフローの構文エラーなし

### 6. **次の確認事項**

1. **GitHub リポジトリ設定**
   ```
   Settings → Actions → General
   - Actions permissions: Allow all actions
   - Workflow permissions: Read and write permissions
   ```

2. **Secrets の確認**
   ```
   Settings → Secrets and variables → Actions
   - CLAUDE_CODE_OAUTH_TOKEN が存在するか
   - 値が正しく設定されているか
   ```

3. **ブランチ保護ルール**
   - master ブランチに保護ルールがないか確認

### 7. **代替案**

もしGitHub Actionsが使えない場合：

1. **ローカル実行**
   ```bash
   ./local_claude_test.sh
   ```

2. **Webhook + 外部サーバー**
   - GitHub Webhooks を設定
   - 外部サーバーでClaude APIを実行

3. **Public リポジトリに変更**
   - 無料でActions使用可能
   - ただしコードが公開される

## 📊 診断チェックリスト

- [ ] Actions タブにワークフローが表示される
- [ ] Issue コメントでワークフローがトリガーされる
- [ ] エラーログが確認できる
- [ ] CLAUDE_CODE_OAUTH_TOKEN が正しく設定されている
- [ ] リポジトリのActions権限が有効
- [ ] 課金制限に引っかかっていない