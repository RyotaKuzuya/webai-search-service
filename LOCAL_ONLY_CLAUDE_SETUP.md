# GitHub Actionsを使わないClaude Max Plan設定

## 概要

GitHub Actionsの課金を完全に回避し、Claude Max PlanのOAuthトークンをローカルのみで使用する設定です。

## セットアップ手順

### 1. Claude CLIのインストール（未インストールの場合）

```bash
curl -fsSL https://cli.claude.ai/install.sh | sh
```

### 2. OAuth認証の設定

```bash
claude setup-token
```

表示されるURLにアクセスして認証を完了します。

### 3. ローカル実行環境の構築

#### A. 自動化スクリプト

```bash
#!/bin/bash
# claude_automation.sh

# Gitの変更を監視
while true; do
    if git diff --quiet HEAD; then
        echo "変更なし"
    else
        echo "変更を検出！"
        # Claudeでコードレビュー
        git diff | claude "このコードの変更をレビューしてください"
    fi
    sleep 30
done
```

#### B. Webhookレシーバー（オプション）

```python
# webhook_receiver.py
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    # Issue作成時
    if data.get('action') == 'opened' and 'issue' in data:
        issue_body = data['issue']['body']
        if '@claude' in issue_body:
            # Claudeで処理
            response = subprocess.run(
                ['claude', issue_body.replace('@claude', '')],
                capture_output=True,
                text=True
            )
            print(f"Claude response: {response.stdout}")
    
    return 'OK', 200

if __name__ == '__main__':
    app.run(port=8080)
```

### 4. GitHub Webhooksの設定（オプション）

1. リポジトリ Settings → Webhooks → Add webhook
2. Payload URL: `https://your-server.com/webhook`
3. Content type: `application/json`
4. Events: Issues, Pull requests

## 使用方法

### 基本的な使い方

```bash
# コードレビュー
claude "simple_api.pyをレビューしてください" --model sonnet-3.5

# 自動改善
claude "エラーハンドリングを改善してください" --model sonnet-3.5

# テスト生成
claude "simple_api.pyのテストを生成してください" --model sonnet-3.5
```

### 高度な使い方

```bash
# ファイル監視と自動レビュー
./claude_file_watcher.sh

# Git commit時の自動レビュー
git config --local core.hooksPath .githooks
```

## メリット

1. **完全無料** - GitHub Actionsを使用しない
2. **高速** - ローカル実行で遅延なし
3. **プライバシー** - データが外部サーバーを経由しない
4. **制限なし** - GitHub Actionsの制限に縛られない

## デメリット

1. **手動実行** - 自動化には工夫が必要
2. **常時稼働が必要** - Webhook受信にはサーバーが必要
3. **チーム共有が困難** - 個人環境に依存

## 推奨される使用シナリオ

- 個人開発プロジェクト
- プライベートリポジトリでの作業
- 機密性の高いコード
- 頻繁な実行が必要な場合