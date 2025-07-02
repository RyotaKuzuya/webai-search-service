# 🚀 WebAI - すぐに動作させる方法

## 今すぐローカルで実行（最速）

```bash
# Python がインストールされている場合
python3 run-local-simple.py

# ブラウザが自動的に開きます: http://localhost:5000
# ログイン: admin / admin123
```

## 本番環境（your-domain.com）で動かす

### 必要なもの
1. **サーバー**: VPS、AWS EC2、DigitalOcean など
2. **ドメイン**: your-domain.comのDNS設定
3. **10分の作業時間**

### 手順
```bash
# 1. サーバーにSSH接続
ssh your-server

# 2. コードをダウンロード
git clone <your-repo> webai
cd webai

# 3. 自動デプロイ実行
./deploy-all.sh

# 完了！ https://your-domain.com でアクセス可能
```

## 無料でクラウドに公開する

### Option 1: Replit（最も簡単）
```bash
./deploy-to-replit.py
# 指示に従ってReplitにアップロード
# URL: https://webai.your-username.repl.co
```

### Option 2: Render.com
```bash
./deploy-to-render.sh
# GitHubと連携して自動デプロイ
# URL: https://webai-app.onrender.com
```

### Option 3: Railway.app
```bash
./deploy-to-railway.sh
# CLIまたはGitHub連携でデプロイ
# URL: https://webai.railway.app
```

## 今すぐ試せるオンラインIDE

### 1. GitHub Codespaces（推奨）
1. このコードをGitHubにプッシュ
2. "Code" → "Codespaces" → "Create codespace"
3. ブラウザ内で即座に開発環境が起動
4. ターミナルで: `python3 run-local-simple.py`

### 2. Gitpod
1. GitHubにプッシュ後
2. https://gitpod.io/#https://github.com/[your-username]/webai
3. 自動的に環境構築完了

### 3. StackBlitz
1. https://stackblitz.com/fork/github/[your-username]/webai
2. ブラウザ内で即座に実行

## Docker を使う場合

```bash
# Dockerがインストール済みなら
./quick-start.sh

# アクセス: http://localhost
```

## トラブルシューティング

### Python がない場合
- Windows: https://python.org からダウンロード
- Mac: `brew install python3`
- Linux: `sudo apt install python3 python3-pip`

### ポートが使用中の場合
`.env` ファイルでポート変更:
```
PORT=8080
```

### その他の問題
```bash
# 診断スクリプト実行
./test-setup.sh

# 詳細ログ確認
python3 run-local-simple.py --debug
```

---

## 🎯 3分で動作確認する最速の方法

1. **このフォルダで実行**:
   ```bash
   python3 run-local-simple.py
   ```

2. **ブラウザが開く**: http://localhost:5000

3. **ログイン**: 
   - Username: `admin`
   - Password: `admin123`

4. **チャットでテスト**!

それだけです！ 🎉