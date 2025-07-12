# 🧪 AI自動改善システム クイックテスト

## テスト方法

### 方法1: シンプルなテストIssue

以下のURLで新しいIssueを作成:
https://github.com/RyotaKuzuya/webai-search-service/issues/new

**タイトル:**
```
テスト: Claude応答確認
```

**本文:**
```
@claude こんにちは！正常に動作しているか確認のため、簡単に応答してください。
```

### 方法2: コード分析リクエスト

**タイトル:**
```
コード品質チェック依頼
```

**本文:**
```
@claude 

simple_api.pyのコードを確認して、以下の点について簡単にコメントしてください：

1. エラーハンドリングは適切か
2. 改善できる点はあるか

簡潔な回答で構いません。
```

### 方法3: AI自動改善ワークフロー実行

1. https://github.com/RyotaKuzuya/webai-search-service/actions
2. 「AI Auto Test & Improvement」を選択
3. 「Run workflow」をクリック
4. Test typeで「full」を選択
5. 「Run workflow」をクリック

## 確認ポイント

- [ ] GitHub Actionsが起動するか
- [ ] @claudeメンションに反応するか
- [ ] エラーメッセージが表示されるか
- [ ] 正常に応答が返ってくるか

## トラブルシューティング

もしエラーが発生した場合：

1. **Actions タブでワークフローのログを確認**
2. **Secretsが正しく設定されているか確認**
   - Settings → Secrets → CLAUDE_CODE_OAUTH_TOKEN
3. **ワークフローファイルの構文エラーがないか確認**