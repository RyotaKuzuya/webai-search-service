# 📝 手動テスト用 Issue テンプレート

## Issue 作成手順

### 1. 新しい Issue を作成
👉 **[ここをクリック](https://github.com/RyotaKuzuya/webai-search-service/issues/new)**

### 2. 以下の内容をコピー＆ペースト

**Title:**
```
Claude Max Plan OAuth Test - Manual
```

**Body:**
```
Testing Claude Code Action with OAuth tokens:
- CLAUDE_ACCESS_TOKEN ✅
- CLAUDE_REFRESH_TOKEN ✅
- CLAUDE_EXPIRES_AT ✅

Manual test at: [現在時刻]
```

### 3. Issue を作成（Create issue ボタン）

### 4. 作成後、コメントを追加

```
@claude

OAuth認証のテストです。このメッセージに応答してください。
```

### 5. 結果を確認

**Actions タブで確認:**
👉 **[GitHub Actions](https://github.com/RyotaKuzuya/webai-search-service/actions)**

---

## 期待される動作

1. **Claude Code Action** が起動
2. Claude がコメントに返信
3. ワークフローが完了

## エラーの場合

- 課金エラー → GitHubアカウントの支払い設定を確認
- 認証エラー → トークンの有効期限を確認
- その他 → Actionsのログを確認