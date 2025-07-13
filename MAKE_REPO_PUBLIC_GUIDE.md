# リポジトリをPublicに変更する手順

## ⚠️ 変更前の確認事項

### 1. セキュリティチェック
- APIキー、パスワード、トークンが含まれていないか
- 個人情報や機密情報が含まれていないか
- .gitignoreが適切に設定されているか

### 2. 現在の.gitignore確認
```bash
cat .gitignore
```

## 📝 変更手順

### ステップ1: GitHubで設定変更

1. リポジトリページにアクセス
   https://github.com/RyotaKuzuya/webai-search-service

2. **Settings** タブをクリック

3. 一番下の **Danger Zone** セクションまでスクロール

4. **Change repository visibility** をクリック

5. **Change visibility** をクリック

6. **Make public** を選択

7. 確認のため以下を入力:
   ```
   RyotaKuzuya/webai-search-service
   ```

8. **I have read and understand these effects** にチェック

9. **Make this repository public** をクリック

## ✅ 変更後の確認

### 1. リポジトリの状態
- URLの横に "Public" と表示される
- 誰でもコードを閲覧可能になる

### 2. GitHub Actions
- **無料で無制限**に使用可能！
- 課金エラーが解消される

## 🎉 Public変更後にできること

### 1. GitHub Actionsを復活
```bash
# アーカイブしたワークフローを復元
mkdir -p .github/workflows
cp .github/workflows-archived/claude-code-actions.yml .github/workflows/
```

### 2. CCAを無料で使用
- Issue/PRで`@claude`メンション
- 自動テスト・改善ワークフロー

## ⚠️ 注意事項

### Publicリポジトリのメリット
- ✅ GitHub Actions完全無料
- ✅ コミュニティからの貢献可能
- ✅ ポートフォリオとして公開

### Publicリポジトリのデメリット
- ⚠️ コードが世界中に公開される
- ⚠️ 機密情報の管理に注意
- ⚠️ ライセンスの明記推奨

## 🔒 セキュリティ対策

### 1. 環境変数の確認
```bash
# .envファイルが.gitignoreに含まれているか確認
grep -E "\.env|config\.json|credentials" .gitignore
```

### 2. Secretsの利用
- GitHub Secretsに機密情報を保存
- コードには含めない

## 📋 チェックリスト

- [ ] .gitignoreが適切に設定されている
- [ ] APIキーやパスワードがコードに含まれていない
- [ ] 個人情報が含まれていない
- [ ] ライセンスファイルを追加する（オプション）
- [ ] READMEが適切に記述されている