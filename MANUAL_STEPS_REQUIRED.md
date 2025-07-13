# 📋 手動で実行が必要な手順

## 1. コードをプッシュ

```bash
cd /home/ubuntu/webai
git push origin master
```

GitHubトークンが無効なため、以下のいずれかの方法でプッシュ：
- SSH認証を設定
- 新しいPersonal Access Tokenを作成
- GitHub Desktop を使用

## 2. プッシュ後のテスト

### Issue #4 にコメント投稿

URL: https://github.com/RyotaKuzuya/webai-search-service/issues/4

コメント内容:
```
@claude

Max Plan サポートのテストです！
Claude Code v1.0.44+ で正常に動作することを確認してください。
```

## 3. 結果確認

- **Actions タブ**: https://github.com/RyotaKuzuya/webai-search-service/actions
- 新しいワークフロー「Claude Max Plan Actions」が実行されるはず

## 📊 現在の状態

- ✅ Claude Code v1.0.51（Max Plan対応）
- ✅ ワークフローファイル作成済み
- ✅ リポジトリPublic
- ✅ CLAUDE_CODE_OAUTH_TOKEN設定済み
- ❌ 最新コードがGitHubに未プッシュ

## 🎯 期待される結果

プッシュ後、@claudeメンションで：
- startup_failureではなく正常実行
- Claudeからの自動返信
- 完全無料での動作

あと一歩で完成です！