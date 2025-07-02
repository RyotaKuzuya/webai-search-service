# WebAI アーキテクチャ設計書

## 概要
WebAIはclaude-code-apiを使用してローカルのClaude Codeと統合し、Web検索機能を持つAIチャットサービスを提供します。

## システム構成

```
┌─────────────────┐
│   ブラウザ      │
│  (HTTPS/WSS)    │
└────────┬────────┘
         │
┌────────▼────────┐
│     Nginx       │ Port 443/80
│  (SSL終端)      │
└────────┬────────┘
         │
┌────────▼────────┐
│   Flask App     │ Port 5000
│  (WebSocket)    │ Docker Container
└────────┬────────┘
         │
┌────────▼────────┐
│ claude-code-api │ Port 8000
│   (FastAPI)     │ Host System
└────────┬────────┘
         │
┌────────▼────────┐
│  Claude Code    │
│   (Local CLI)   │ Host System
└─────────────────┘
```

## 重要な設計変更

### 1. claude-code-apiをホストで実行
- Dockerコンテナ内ではなく、ホストシステムで直接実行
- ローカルのclaude codeへの直接アクセスが可能
- 認証情報（~/.claude）を共有

### 2. Flask AppからホストAPIへの接続
- DockerコンテナからホストのAPIに接続
- `host.docker.internal:8000`を使用

### 3. ストリーミング対応
- claude-code-apiのストリーミングレスポンスをWebSocketで転送
- リアルタイムでユーザーに表示

## 実装手順

### Phase 1: claude-code-apiのセットアップ
1. GitHubからクローン
2. 依存関係のインストール
3. ホストでサービス起動

### Phase 2: Flask Appの修正
1. claude-code-apiのエンドポイントを使用
2. OpenAI互換APIの実装
3. ストリーミングレスポンスの処理

### Phase 3: 統合テスト
1. エンドツーエンドの動作確認
2. エラーハンドリングの実装
3. パフォーマンス最適化

## セキュリティ考慮事項
- claude-code-apiはlocalhost:8000でのみリッスン
- Nginxで外部アクセスを制限
- 認証情報はDockerコンテナから隔離