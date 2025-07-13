# Claude Code Actions 最終テスト手順

## 🧪 テスト方法

### 1. 新しいIssueを作成

**URL**: https://github.com/RyotaKuzuya/webai-search-service/issues/new

**タイトル**:
```
Public化成功テスト - Claude Code Actions動作確認
```

**本文**:
```
リポジトリがPublicになりました！無料でGitHub Actionsが使えるはずです。

以下でテストします。
```

### 2. Issueを作成後、コメントを追加

**コメント1**:
```
@claude

こんにちは！正常に動作していますか？

このリポジトリ（webai-search-service）について簡単に説明してください。
```

### 3. 確認ポイント

- [ ] GitHub Actions が起動する
- [ ] 課金エラーが出ない
- [ ] Claudeから返信が来る

### 4. GitHub Actionsの確認

**URL**: https://github.com/RyotaKuzuya/webai-search-service/actions

- ワークフローが実行されているか確認
- エラーが出ていないか確認

## 📊 期待される結果

1. **課金エラーなし** - Publicリポジトリなので無料
2. **Claude応答あり** - OAuthトークンが正しければ応答
3. **即座に実行** - 待機時間なし

## ⚠️ もしエラーが出た場合

### OAuthトークンエラーの場合
1. 新しいトークンを生成: `claude setup-token`
2. GitHub Secretsを更新: `CLAUDE_CODE_OAUTH_TOKEN`

### ワークフローが起動しない場合
1. Actions権限を確認
2. ワークフローファイルの構文を確認

## 🎯 テスト成功の基準

- GitHub Actionsが無料で実行される ✅
- Claudeが@メンションに応答する ✅
- エラーメッセージが表示されない ✅