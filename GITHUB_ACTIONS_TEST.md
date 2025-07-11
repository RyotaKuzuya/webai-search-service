# GitHub Actions テスト手順

WebAI API統合のGitHub Actionsをテストする手順です。

## 1. ブラウザでGitHub Actionsページを開く

https://github.com/RyotaKuzuya/webai-search-service/actions

## 2. ワークフローを手動実行

1. 左側のワークフロー一覧から「Claude WebAI Webhook Trigger」を選択
2. 右側の「Run workflow」ボタンをクリック
3. 以下を入力：
   - Branch: `test-claude-actions`
   - Claude に実行させるタスク: `WebAI APIの動作確認テストです。日本語で簡単に返答してください。`
   - 使用するモデル: `opus4`
4. 「Run workflow」ボタンをクリック

## 3. 実行結果を確認

- ワークフローの実行状況がリアルタイムで表示されます
- 成功すると緑のチェックマークが表示されます
- クリックして詳細ログを確認できます

## 4. Issueコメントでのテスト

1. https://github.com/RyotaKuzuya/webai-search-service/issues/2
2. 以下のようにコメント：
   ```
   @claude WebAIプロジェクトの現在の状態を教えてください
   ```
3. GitHub Actionsが自動的に起動し、Claudeの応答がコメントとして追加されます

## トラブルシューティング

### エラーが発生した場合

1. **API接続エラー**: 
   - NGINXが正しく設定されているか確認
   - `sudo systemctl status nginx`
   - `curl https://your-domain.com/api/simple/health`

2. **認証エラー**:
   - WebAIサービスが起動しているか確認
   - `ps aux | grep simple_api.py`

3. **タイムアウト**:
   - NGINXのタイムアウト設定を確認（30分に設定済み）
   - Claude APIの負荷状況を確認

## 成功例

正常に動作した場合、以下のような応答が表示されます：

```
## 🤖 Claude WebAI Response

WebAI APIは正常に動作しています。このメッセージが表示されているということは、
GitHub ActionsからWebAI経由でClaude APIへの接続が成功し、日本語での応答が
正しく返されていることを意味します。テストは成功です！
```