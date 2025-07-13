# ⚠️ 重要：Claude Max は GitHub Actions で使用不可

## 公式回答（Anthropic開発者より）

> "Currently we don't support Claude Max in the GitHub action. You'll need to create an API key via console.anthropic.com in order to use the action."

**つまり：Claude Max Plan は GitHub Actions では使えません。**

## 📊 現状の整理

### ❌ 動作しないもの
- Claude Max Plan のOAuthトークン
- `CLAUDE_CODE_OAUTH_TOKEN` での認証

### ✅ 動作するもの
- console.anthropic.com で作成したAPIキー
- 従量課金のAPIキー（sk-ant-api...）

## 🔧 解決方法

### オプション1：APIキーを作成（有料）
1. https://console.anthropic.com にアクセス
2. APIキーを作成
3. GitHub Secretsに `ANTHROPIC_API_KEY` として設定
4. **注意：使用した分だけ課金される**

### オプション2：ローカル実行のみ（無料）
```bash
# Claude Max Planで無料
./local_claude_test.sh
./claude_file_watcher.sh
```

### オプション3：Self-hosted Runner（複雑）
- 自分のサーバーでGitHub Runnerを動かす
- Claude Codeをインストール
- Max Planの認証を使用

## 💡 結論

**GitHub Actions で Claude を無料で使うことはできません。**

選択肢：
1. APIキーで従量課金（GitHub Actions使用）
2. ローカル実行のみ（Max Planで無料）
3. GitHub Actions自体を使わない

## 📝 推奨

コスト0円を維持したい場合：
- **GitHub Actionsは諦めて、ローカル実行のみ使用**
- すでに作成済みのローカルスクリプトを活用

```bash
# 完全無料で使用可能
./local_claude_test.sh
```