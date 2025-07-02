# 重要：WebAIを実際に動作させるための手順

## 現在の状況
- ✅ 全ての必要なファイルとスクリプトは作成済み
- ❌ 実際のサーバーへのデプロイはまだ行われていない
- ❌ your-domain.comドメインは設定されていない

## 実際に動作させるために必要な作業

### 1. サーバーの準備
実際のサーバー（VPS、EC2、など）が必要です：
- Ubuntu 20.04以上
- 最低2GB RAM
- 20GB以上のディスク容量
- グローバルIPアドレス

### 2. ドメインのDNS設定
your-domain.comのDNS管理画面で：
```
Aレコード: your-domain.com → [サーバーのIPアドレス]
Aレコード: www.your-domain.com → [サーバーのIPアドレス]
```

### 3. サーバーへのファイル転送
```bash
# ローカルからサーバーへ全ファイルをコピー
scp -r /home/ubuntu/webai username@your-server-ip:/home/username/

# またはGit経由
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 4. サーバーでの実行

サーバーにSSH接続して：

```bash
# 1. サーバーにログイン
ssh username@your-server-ip

# 2. プロジェクトディレクトリへ移動
cd /home/username/webai

# 3. Dockerをインストール
sudo ./install-docker.sh
# ログアウトして再ログイン、または
newgrp docker

# 4. 環境設定
cp .env.sample .env
nano .env  # 必要な値を設定

# 5. OAuth設定（開発用モック認証）
./setup-oauth.sh
# オプション2を選択

# 6. デプロイ実行
./deploy-all.sh
```

## ローカルでテストする方法

実際のサーバーがない場合、ローカルでテスト可能です：

### 方法1: ローカルDocker環境でテスト
```bash
# 1. 開発環境セットアップ
./setup-dev.sh

# 2. Docker起動
docker-compose up

# 3. ブラウザでアクセス
http://localhost
```

### 方法2: Docker Desktopを使用
1. Docker Desktopをインストール
2. プロジェクトフォルダで以下を実行：
```bash
./quick-start.sh
```

## トラブルシューティング

### Dockerがインストールできない場合
```bash
# WSL2 (Windows)の場合
wsl --install
# Docker Desktopをインストール

# Macの場合
brew install docker
brew install docker-compose
```

### ポート競合の場合
```bash
# 使用中のポートを確認
sudo lsof -i :80
sudo lsof -i :443

# docker-compose.ymlでポートを変更
ports:
  - "8080:80"  # 80の代わりに8080を使用
```

## 実際のサーバーなしでデモする方法

### 1. ngrokを使用（一時的な公開URL）
```bash
# ngrokをインストール
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# ローカルサービスを公開
ngrok http 80
```

### 2. Gitpod/CodeSpacesを使用
- GitHubにコードをプッシュ
- Gitpod/CodeSpacesで開く
- 自動的に公開URLが提供される

## 次のステップ

1. **実際のサーバーを用意する**
   - AWS EC2
   - DigitalOcean
   - Vultr
   - さくらVPS など

2. **ドメインを設定する**
   - DNS Aレコードを設定
   - 約15分待つ（DNS伝播）

3. **本番デプロイを実行**
   - サーバーで`./deploy-all.sh`を実行

4. **動作確認**
   - https://your-domain.com にアクセス
   - 管理者ログインでテスト

---

現在作成されたファイルは全て正しく動作するように設計されていますが、
実際のサーバーとドメイン設定が必要です。