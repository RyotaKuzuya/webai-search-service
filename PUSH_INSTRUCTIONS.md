# GitHubへのプッシュ手順

## 現在の状況
- GitHubトークンが無効
- SSHキーが設定されていない
- プッシュする必要があるコミットが存在

## プッシュ方法

### オプション1: 新しいトークンを作成
1. https://github.com/settings/tokens/new
2. 必要な権限: `repo` (Full control of private repositories)
3. トークンを生成
4. 以下のコマンドを実行:
```bash
git remote set-url origin https://YOUR_NEW_TOKEN@github.com/RyotaKuzuya/webai-search-service.git
git push origin master
```

### オプション2: GitHub Desktop を使用
1. GitHub Desktop をダウンロード
2. リポジトリを追加
3. 「Push origin」をクリック

### オプション3: パッチファイルを適用
現在の変更内容は `latest_changes.patch` に保存されています。
別の環境で:
```bash
git apply latest_changes.patch
git push origin master
```

## プッシュ後のテスト

1. Issue #4 にアクセス: https://github.com/RyotaKuzuya/webai-search-service/issues/4

2. 以下のコメントを投稿:
```
@claude

Max Plan (v1.0.44+) でのテストです！
正常に動作することを確認してください。
```

3. 確認場所:
   - Actions: https://github.com/RyotaKuzuya/webai-search-service/actions
   - 新しいワークフローが実行されるはず

## 最新のコミット内容

- ✅ Claude Max Plan サポートを有効化
- ✅ 新しいワークフロー: `.github/workflows/claude-max-plan.yml`
- ✅ OAuthトークン認証を使用
- ✅ 完全無料での動作が可能