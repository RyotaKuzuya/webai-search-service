# WebAI Search Service

リアルタイムWeb検索と連携するAIチャットサービス

## 概要

WebAI Search Serviceは、claude-code-apiをエンジンとし、WebSocket/SSEでリアルタイムストリーミング表示を実現するAIチャットサービスです。Web検索機能により最新情報を取得し、包括的な回答を提供します。

## 主な機能

- **リアルタイムAIチャット**: WebSocketを使用したリアルタイムストリーミング応答
- **Web検索連携**: AIによる自律的Web検索実行と複数Webページ情報の要約・統合
- **セキュアなアクセス**: SSL/TLS暗号化通信と管理者認証
- **OAuth認証**: claude-code-apiのOAuth認証フロー対応
- **永続的認証**: Dockerボリュームによる認証情報の永続化
- **Claude Codeローカル実行**: GitHub Actions課金制限を回避したローカル実行

## システムアーキテクチャ

```
┌─────────────────┐
│   ブラウザ      │
│  (Frontend)     │
└────────┬────────┘
         │ HTTPS/WSS
         │
┌────────▼────────┐
│     Nginx       │
│ (Reverse Proxy) │
└────────┬────────┘
         │
┌────────▼────────┐
│   WebAI App     │
│   (Flask +      │
│   SocketIO)     │
└────────┬────────┘
         │ HTTP API
         │
┌────────▼────────┐
│   AgentAPI      │
│ (HTTP API for   │
│ Claude Code)    │
└─────────────────┘
```

## 技術スタック

- **AIエンジン**: claude-code-api
- **API化ミドルウェア**: AgentAPI (HTTP API for Claude Code)
- **Backend**: Python 3.11+, Flask, Flask-SocketIO
- **Frontend**: HTML5, JavaScript, WebSocket
- **Web Server**: Nginx
- **SSL/TLS**: Let's Encrypt (Certbot)
- **Container**: Docker & Docker Compose (必須)

## ディレクトリ構造

```
webai/
├── backend/              # Flask アプリケーション
│   ├── app.py           # メインアプリケーション
│   ├── requirements.txt # Python依存関係
│   └── templates/       # HTMLテンプレート
├── frontend/            # HTML/CSS/JavaScript
│   ├── css/            # スタイルシート
│   └── js/             # JavaScriptファイル
├── nginx/              # Nginx設定
│   ├── nginx.conf      # メイン設定
│   └── conf.d/         # サイト設定
├── docker-compose.yml  # Docker構成
├── docker-compose.prod.yml # 本番用Docker構成
├── Dockerfile          # アプリケーションコンテナ
├── .env.sample         # 環境変数テンプレート
├── .gitignore          # Git除外設定
├── setup-oauth.sh      # OAuth認証セットアップ
├── CLAUDE.md           # プロジェクト要件定義
├── DEPLOYMENT.md       # デプロイメント手順
└── README.md           # このファイル
```

## クイックスタート

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd webai
```

### 2. 環境変数の設定

```bash
cp .env.sample .env
nano .env  # 必要な値を設定
```

### 3. OAuth認証のセットアップ

```bash
./setup-oauth.sh
```

### 4. Docker Composeで起動

```bash
docker-compose up -d
```

### 5. ブラウザでアクセス

```
https://your-domain.com
```

## 詳細なセットアップ

詳細なデプロイメント手順については、[DEPLOYMENT.md](./DEPLOYMENT.md)を参照してください。

## 環境変数

`.env.sample`を参考に以下の環境変数を設定:

- `SECRET_KEY`: Flask用のシークレットキー
- `ADMIN_USERNAME`: 管理者ユーザー名
- `ADMIN_PASSWORD`: 管理者パスワード
- `DOMAIN_NAME`: ドメイン名
- `LETSENCRYPT_EMAIL`: Let's Encrypt通知用メール

## セキュリティ考慮事項

1. **OAuth認証**
   - claude-code-apiはOAuth認証フローを使用
   - 認証情報は`./claude-config/`に永続化

2. **通信の暗号化**
   - 全ての通信はHTTPS/WSSで暗号化
   - Let's Encryptによる自動証明書更新

3. **アクセス制限**
   - 単一管理者アカウントのみログイン可能
   - セッションベースの認証

## 開発環境での実行

```bash
# 開発用設定に切り替え
mv nginx/conf.d/webai.conf nginx/conf.d/webai.conf.prod
mv nginx/conf.d/webai-dev.conf nginx/conf.d/webai.conf

# 環境変数設定
export FLASK_ENV=development

# 起動
docker-compose up
```

## トラブルシューティング

### 認証エラー

```bash
# OAuth認証の再実行
./setup-oauth.sh

# 認証ファイルの確認
ls -la ./claude-config/
```

### ログの確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f webapp
docker-compose logs -f claude-api
```

### コンテナの再起動

```bash
docker-compose restart webapp
```

## メンテナンス

### バックアップ

```bash
tar -czf webai-backup-$(date +%Y%m%d).tar.gz \
  .env \
  claude-config/ \
  certbot/conf/
```

### アップデート

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

## ライセンス

このプロジェクトは内部使用を目的としています。

## サポート

問題が発生した場合は、[DEPLOYMENT.md](./DEPLOYMENT.md)のトラブルシューティングセクションを参照してください。

## Claude Code GitHub Actions (公式)

Claude MaxプランでGitHub Actionsが利用可能です：

### セットアップ

```bash
# OAuthトークンの生成
./setup_claude_oauth_token.sh

# GitHub Secretsに追加
CLAUDE_CODE_OAUTH_TOKEN
```

### 使用方法

1. **Issue/PRでのメンション**
   ```
   @claude このコードをレビューしてください
   ```

2. **手動実行**
   - Actions → Claude Code Official → Run workflow

### ローカル実行（バックアップ）

```bash
# メニュー式の実行
./claude_local_executor.sh

# Claude CLI直接
claude "コードレビューをしてください" --model sonnet4
```

詳細は[GITHUB_ACTIONS_LOCAL.md](GITHUB_ACTIONS_LOCAL.md)を参照してください。

## AI自動改善システム

### 概要

AI自動改善システムは、Claude Code Actionsを活用してアプリケーションを自動的にテスト・評価・改善する仕組みです。

### 機能

1. **定期的な健全性チェック**（毎日深夜2時）
   - APIエンドポイントの可用性確認
   - レスポンスタイムの測定
   - エラーログの分析

2. **継続的モニタリング**（1時間ごと）
   - システムメトリクスの収集
   - パフォーマンス劣化の検出
   - アラート条件に基づくIssue作成

3. **自動改善**
   - 問題検出時に@claudeメンション付きIssueを自動作成
   - Claude Code Actionsが問題を分析し改善PRを作成

### セットアップ

```bash
# 必要なGitHubラベルの作成
./setup_ai_improvement_labels.sh

# GitHub Secretsの設定
# CLAUDE_API_KEY: Claude APIキー
# GITHUB_TOKEN: 自動で提供される
```

### テスト実行

```bash
# AI自動改善システムのテスト
./test_ai_improvement.sh
```

### ワークフロー

- **AI Auto Test & Improvement**: 定期実行または手動実行でアプリケーションをテスト
- **Continuous Monitoring & Feedback**: 1時間ごとのメトリクス収集とアラート
- **Claude Code Actions**: @claudeメンションでAIによる問題解決

### モニタリング

- [GitHub Actions](https://github.com/RyotaKuzuya/webai-search-service/actions)
- [Issues](https://github.com/RyotaKuzuya/webai-search-service/issues)
- [Pull Requests](https://github.com/RyotaKuzuya/webai-search-service/pulls)