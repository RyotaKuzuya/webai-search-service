# WebAI Search Service 環境構築手順書

## 1. 概要

このドキュメントでは、WebAI Search Serviceの環境構築手順を説明します。

## 2. 前提条件

- Ubuntu 22.04 LTS
- Python 3.10以上
- Git
- sudo権限を持つユーザー

## 3. セットアップ手順

### 3.1. 基本的なシステムパッケージのインストール

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx
```

### 3.2. Claude Codeのセットアップ

#### 3.2.1. Claude Codeのインストール

```bash
# Claude Codeをインストール（未インストールの場合）
npm install -g @anthropic-ai/claude-code

# インストール確認
claude --version
```

#### 3.2.2. Claude認証設定

```bash
# 認証設定スクリプトの実行
cd /home/ubuntu/webai
chmod +x setup-claude-api.sh
./setup-claude-api.sh
```

**Claude認証手順:**
1. `claude login` コマンドを実行
2. 表示される認証 URLをコピーしてブラウザで開く
3. Anthropicアカウントでログインして認証を許可
4. 表示される認証コードをターミナルに貼り付け

**重要**: 認証情報は `~/.config/claude/` に保存されます。
Dockerを使用する場合は、このディレクトリをボリュームマウントして永続化してください。

### 3.3. WebAIアプリケーションのセットアップ

```bash
cd /home/ubuntu/webai

# 環境変数の設定
cp .env.example .env
nano .env  # 必要に応じて編集

# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# 起動スクリプトの実行権限付与
chmod +x start-webai.sh
```

### 3.4. SSL証明書の取得（Let's Encrypt）

```bash
# Nginxを一時停止
sudo systemctl stop nginx

# 証明書の取得
sudo certbot certonly --standalone -d your-domain.com

# Nginxを再起動
sudo systemctl start nginx
```

### 3.5. Nginxの設定

```bash
# 既存の設定をバックアップ
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# WebAI用の設定をコピー
sudo cp /home/ubuntu/webai/nginx/conf.d/webai.conf /etc/nginx/sites-available/webai

# シンボリックリンクを作成
sudo ln -s /etc/nginx/sites-available/webai /etc/nginx/sites-enabled/webai

# デフォルト設定を無効化
sudo rm /etc/nginx/sites-enabled/default

# 設定をテスト
sudo nginx -t

# Nginxを再起動
sudo systemctl restart nginx
```

### 3.6. systemdサービスの設定（本番環境用）

```bash
# サービスファイルの作成
sudo nano /etc/systemd/system/webai.service
```

以下の内容を貼り付け:

```ini
[Unit]
Description=WebAI Search Service
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/webai
Environment="PATH=/home/ubuntu/webai/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/ubuntu/webai/.env
ExecStart=/home/ubuntu/webai/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# サービスの有効化と起動
sudo systemctl daemon-reload
sudo systemctl enable webai
sudo systemctl start webai

# ステータス確認
sudo systemctl status webai
```

## 4. Docker環境での実行（推奨）

### 4.1. Dockerのインストール

```bash
# Dockerのインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# 再ログインまたは
newgrp docker
```

### 4.2. Docker Composeでの起動

```bash
cd /home/ubuntu/webai

# 環境変数の設定
cp .env.example .env
nano .env  # 必要に応じて編集

# ビルドと起動
docker-compose up -d

# ログの確認
docker-compose logs -f
```

## 5. 認証トークンの永続化

**重要**: claude-code-apiの認証情報は以下の場所に保存されます:

- **ローカル環境**: `~/.config/claude/claude_config.json`
- **Docker環境**: Dockerボリューム `claude-auth` 内

### バックアップ方法:

```bash
# ローカル環境
cp -r ~/.config/claude ~/claude-config-backup

# Docker環境
docker run --rm -v webai_claude-auth:/data -v $(pwd):/backup alpine tar -czf /backup/claude-auth-backup.tar.gz -C /data .
```

## 6. トラブルシューティング

### ポート競合

```bash
# 使用中のポートを確認
sudo ss -tuln | grep -E ":(80|443|5000|8000)"

# 必要に応じてプロセスを停止
sudo kill <PID>
```

### ログの確認

```bash
# アプリケーションログ
journalctl -u webai -f

# Nginxログ
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Dockerログ
docker-compose logs -f webai
```

### SSL証明書の更新

```bash
# 自動更新のテスト
sudo certbot renew --dry-run

# 手動更新
sudo certbot renew
```

## 7. セキュリティ設定

### ファイアウォール設定

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 環境変数の保護

```bash
chmod 600 /home/ubuntu/webai/.env
```

## 8. メンテナンス

### アップデート手順

```bash
cd /home/ubuntu/webai
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### バックアップ

```bash
# 設定とデータのバックアップ
tar -czf webai-backup-$(date +%Y%m%d).tar.gz webai/ webai-claude-api/
```

## 9. 動作確認

1. ブラウザで https://your-domain.com にアクセス
2. 管理者アカウントでログイン
3. 質問を入力して送信
4. リアルタイムで処理状況が表示されることを確認

---

本手順書に従って環境構築を行えば、WebAI Search Serviceが正常に動作します。
問題が発生した場合は、ログを確認し、必要に応じて設定を見直してください。