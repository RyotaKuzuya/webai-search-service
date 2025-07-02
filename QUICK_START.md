# WebAI サービス クイックスタートガイド

## 現在の状況
your-domain.comにアクセスできない状態です。以下の手順でサービスを起動してください。

## 手動セットアップ手順

### 1. ターミナルを開いて以下のコマンドを実行

```bash
# ディレクトリに移動
cd /home/ubuntu

# スクリプトに実行権限を付与
chmod +x install-and-start-webai.sh

# インストールと起動
sudo ./install-and-start-webai.sh
```

### 2. 別の方法（スクリプトが動作しない場合）

#### Step 1: 必要なパッケージをインストール
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
```

#### Step 2: WebAIディレクトリで作業
```bash
cd /home/ubuntu/webai

# Python仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

#### Step 3: Nginxを設定
```bash
# Nginx設定ファイルを作成
sudo nano /etc/nginx/sites-available/webai
```

以下の内容を貼り付け:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# サイトを有効化
sudo ln -s /etc/nginx/sites-available/webai /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 4: WebAIを起動
```bash
cd /home/ubuntu/webai
source venv/bin/activate

# 直接起動（テスト用）
python app.py

# またはGunicornで起動（本番用）
gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
```

### 3. 動作確認

1. ブラウザで http://your-domain.com にアクセス
2. ログイン画面が表示されれば成功
   - ユーザー名: admin
   - パスワード: webai2024secure

### 4. トラブルシューティング

#### ポート確認
```bash
# 使用中のポートを確認
sudo lsof -i :80
sudo lsof -i :5000
```

#### プロセス確認
```bash
# Nginxの状態
sudo systemctl status nginx

# Python プロセス
ps aux | grep python
```

#### ログ確認
```bash
# Nginxエラーログ
sudo tail -f /var/log/nginx/error.log

# アクセスログ
sudo tail -f /var/log/nginx/access.log
```

## 重要な注意事項

1. **Claude Codeのインストール**
   - WebAIはClaude Codeを使用します
   - 未インストールの場合: `sudo npm install -g @anthropic-ai/claude-code`
   - 認証: `claude login`

2. **ファイアウォール**
   - ポート80と443が開いていることを確認
   - `sudo ufw allow 80/tcp`
   - `sudo ufw allow 443/tcp`

3. **SSL証明書（HTTPS）**
   - 現在はHTTPで動作
   - HTTPS化: `sudo certbot --nginx -d your-domain.com`

## 緊急時の対応

もし上記の手順でも動作しない場合は、以下を確認してください：

1. エラーメッセージの確認
2. ディレクトリとファイルの存在確認
3. Pythonバージョン（3.8以上が必要）
4. ネットワーク接続状態

---

このガイドに従ってセットアップを行えば、your-domain.comでWebAIサービスにアクセスできるようになります。