# WebAI検索サービス - プロジェクト開発ガイド

## プロジェクト概要
リアルタイムWeb検索と連携するAIチャットサービス。claude-code-apiをエンジンとし、WebSocket/SSEでリアルタイムストリーミング表示を実現。

## 技術スタック
- **AIエンジン:** claude-code-api
- **API化ミドルウェア:** AgentAPI (HTTP API for Claude Code)
- **Web検索機能:** Claude Search MCP Server
- **Webアプリケーション:** Flask
- **リアルタイム通信:** WebSocket または Server-Sent Events (SSE)
- **Webサーバー:** Nginx
- **SSL/TLS:** Let's Encrypt (Certbot)
- **実行環境:** Docker / Docker Compose (必須)

## 主要機能要件

### 1. ログイン機能
- 単一管理者アカウントのみ
- ID/パスワードは環境変数(.env)から読み込み
- サーバーサイドセッション管理

### 2. AIチャットUI
- シンプルで直感的なチャットUI
- 時系列でチャットログ形式表示

### 3. Web検索連携
- AIによる自律的Web検索実行
- 複数Webページ情報の要約・統合

### 4. リアルタイム進捗ストリーミング
- WebSocket/SSEによる持続的接続
- AIの思考プロセスをリアルタイム表示
- claude-code-apiの標準出力をキャプチャ・転送

## 重要な実装要件

### インフラ・デプロイ
- **【最重要】** 既存のclaude-gate, claude-code-api設定を完全削除してクリーンな状態から開始
- Docker Composeによるコンテナ化必須
- Nginxをリバースプロキシとして構成
- your-domain.comドメインでHTTPS(443)対応

### OAuth認証フロー
**注意：APIキーではなくOAuth認証フローを使用**

1. 開発者：claude-code-api初期セットアップ実行
2. 開発者：認証URLを発注者に提示
3. 発注者：Anthropicアカウントで認証許可
4. 発注者：認証コードを開発者に提供
5. 開発者：認証コード入力でセットアップ完了

### 【最重要】認証トークンの永続化
- 認証情報ファイル（~/.config/claude/claude_config.json）の永続化必須
- DockerボリュームマウントでホストOSの永続ディレクトリにマッピング
- コンテナ再起動後も認証情報を保持

## 開発時の注意事項

### アンチパターンを避ける
1. **APIキーの誤用禁止**
   - 従量課金用APIキーではなくOAuth認証フロー使用
   
2. **自動生成スクリプト避ける**
   - Docker Composeによる宣言的環境構築を徹底
   - 手動での構築・検証ステップを省略しない
   
3. **認証情報の揮発防止**
   - 必ずホストOSの永続領域にボリュームマウント

## セキュリティ要件
- 全通信HTTPS暗号化
- 管理者認証情報は環境変数管理
- claude-code-apiは非rootユーザーで実行

## パフォーマンス目標
- 初期応答性：3秒以内
- 最終回答まで：60秒以内

## よく使用するコマンド

### 開発・テスト
```bash
# Docker Compose起動
docker-compose up -d

# Docker Compose停止
docker-compose down

# ログ確認
docker-compose logs -f

# コンテナ状態確認
docker-compose ps
```

### デプロイ
```bash
# 本番環境用Docker Compose起動
docker-compose -f docker-compose.prod.yml up -d

# SSL証明書更新
docker-compose exec certbot certbot renew
```

## 納品物
- ソースコード一式（バックエンド・フロントエンド）
- インフラ構成ファイル（Dockerfile, docker-compose.yml, nginx.conf, .env.sample）
- ドキュメント（環境構築・デプロイ手順書、要件定義書最終版）

## ディレクトリ構造
```
webai/
├── backend/           # Flask アプリケーション
├── frontend/          # HTML/CSS/JavaScript
├── nginx/             # Nginx設定
├── docker-compose.yml # Docker構成
├── Dockerfile         # アプリケーションコンテナ
├── .env.sample        # 環境変数テンプレート
├── CLAUDE.md          # このファイル
└── README.md          # プロジェクト説明
```

## 利用するOSSプロジェクト

### AgentAPI (coder/agentapi)
- **目的:** Claude Code をHTTP APIで制御
- **機能:** ターミナルエミュレーターでAPIコールをキーストロークに変換
- **エンドポイント:** `/messages`, `/message`, `/status`, `/events`
- **GitHub:** https://github.com/coder/agentapi

### Claude Search MCP (doriandarko/claude-search-mcp)
- **目的:** Claude APIを使用したWeb検索機能提供
- **機能:** Model Context Protocol (MCP) サーバー
- **設定可能項目:**
  - 最大検索結果数
  - ドメインフィルタリング（許可/ブロック）
- **要件:** Node.js 18+, Anthropic API key
- **GitHub:** https://github.com/doriandarko/claude-search-mcp

### 代替選択肢

#### Claude API (KoushikNavuluri/Claude-API)
- **目的:** 非公式Claude AI API
- **機能:** Python向けプログラマティック操作
- **特徴:** 会話管理、ファイル添付、履歴取得
- **認証:** Claude AIクッキー必要
- **GitHub:** https://github.com/KoushikNavuluri/Claude-API

#### Claude AI Toolkit (RMNCLDYO/claude-ai-toolkit)
- **目的:** 軽量Python APIラッパー＋CLI
- **対象:** Anthropic公式Claude言語モデル
- **GitHub:** https://github.com/RMNCLDYO/claude-ai-toolkit

## 推奨アーキテクチャ

**AgentAPI + Claude Search MCP** の組み合わせを推奨：

1. **AgentAPI** でClaude CodeのHTTP API化
2. **Claude Search MCP** でWeb検索機能追加
3. **Flask** でこれらをラップしてWebSocket/SSEストリーミング実装

この構成により要件定義書の「claude-code-apiをエンジンとし、WebSocket/SSEでリアルタイムストリーミング表示」が実現可能。

## 実現可能性の検証結果

### ✅ 実現可能な要素

1. **claude-code-apiのWeb検索機能**
   - 内蔵のWebSearchツール（web_search_20250305）が利用可能
   - Claude 3.7 Sonnet、Claude 3.5 Sonnet、Claude 3.5 Haikuで対応
   - ドメインフィルタリング、検索結果数制限などの設定可能

2. **OAuth認証フロー**
   - PKCE OAuth flowを使用（client ID: 9d1c250a-e61b-44d9-88ed-5944d1962f5e）
   - 認証情報は~/.config/claude/claude_config.jsonに保存
   - リフレッシュトークンによる自動再認証対応

3. **Docker環境での認証永続化**
   - claude-dockerプロジェクトで実証済み
   - ~/.claude-docker/claude-home/をボリュームマウント
   - 「Login once, use forever」を実現

4. **AgentAPIによるHTTP API化**
   - ターミナルエミュレーターでClaude Codeを制御
   - `/messages`, `/message`, `/status`, `/events`エンドポイント提供
   - リアルタイムイベントストリーミング対応

### ⚠️ 注意が必要な要素

1. **MCP (Model Context Protocol) 統合**
   - Claude Search MCPはClaude Desktop app向け設計
   - Web API環境での統合には追加開発が必要
   - 既存のWebSearchツールで代替可能

2. **認証の複雑性**
   - OAuth認証の初回設定は手動プロセス必須
   - ブラウザベースの認証フローをCLI環境で実行
   - 認証エラー処理の実装が重要

3. **Dockerセキュリティ**
   - 認証トークンのボリュームマウントはセキュリティリスク
   - 適切な権限設定（600）とUID/GIDマッピングが必要
   - コンテナ内で非rootユーザー実行を推奨

### 📋 推奨実装方針

1. **既存のapp_claude_api.pyベースで開発**
   - すでにFlask + WebSocket/SSE実装済み
   - WebSearch機能のプロンプト強化も実装済み
   - http://localhost:8000/v1/chat/completionsエンドポイント利用

2. **AgentAPIは補助的に利用**
   - 直接的なCLI制御が必要な場合のみ使用
   - 主要機能は既存実装で十分カバー可能

3. **Docker永続化の実装**
   ```yaml
   volumes:
     - ./claude-config:/home/app/.config/claude
     - ./claude-home:/home/app/.claude-docker/claude-home
   ```

4. **セキュリティ強化**
   - 認証情報の暗号化検討
   - 定期的なトークンローテーション
   - アクセスログの実装

この検証により、CLAUDE.mdに記載された要件は**技術的に実現可能**であることが確認されました。

## HTTPS API実装方法

### localhost:8000からHTTPSへの変換

claude-code-apiのデフォルトエンドポイント（http://localhost:8000）をHTTPS対応にする方法：

### 1. **Nginx SSL Reverse Proxy方式**（推奨）

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. **Docker Compose構成**

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - webapp
      
  webapp:
    build: .
    expose:
      - "8000"
    volumes:
      - ./claude-config:/home/app/.config/claude
      
  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
```

### 3. **ローカル開発用自己署名証明書**

```bash
# mkcert使用（推奨）
mkcert -install
mkcert localhost 127.0.0.1 ::1

# または OpenSSL使用
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout localhost.key -out localhost.crt
```

### 4. **Flask直接HTTPS対応**（開発環境のみ）

```python
if __name__ == '__main__':
    app.run(ssl_context='adhoc', host='0.0.0.0', port=8443)
    # または
    app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=8443)
```

### 実装上の注意点

1. **SSL証明書の管理**
   - Let's EncryptでドメインSSL証明書取得
   - Certbotで自動更新設定
   - ローカル開発はmkcertで自己署名証明書

2. **セキュリティ設定**
   - SSL/TLSプロトコルバージョン制限
   - 暗号スイートの適切な選択
   - HSTSヘッダーの設定

3. **パフォーマンス最適化**
   - HTTP/2有効化
   - SSL Session Cache設定
   - Keep-Alive接続の調整

この方法により、claude-code-apiのHTTPエンドポイントを安全なHTTPS APIとして公開できます。