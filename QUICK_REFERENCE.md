# WebAI クイックリファレンス

## 🚀 即座に実行

### ローカルで今すぐ動かす（Docker不要）
```bash
python3 run-local-simple.py
# → http://localhost:5000
# ログイン: admin / admin123
```

### インスタントデモ
```bash
./instant-demo.sh
# 利用可能な方法を自動検出して提案
```

## ☁️ クラウドデプロイ（無料）

### Replit
```bash
./deploy-to-replit.py
# → https://webai.YOUR-USERNAME.repl.co
```

### Render
```bash
./deploy-to-render.sh
# → https://webai-app.onrender.com
```

### Railway
```bash
./deploy-to-railway.sh
# → https://webai.railway.app
```

## 🏢 本番環境（your-domain.com）

### 完全自動デプロイ
```bash
./deploy-all.sh
# DNS設定、SSL取得、全サービス起動を自動実行
```

### 個別デプロイ
```bash
./deploy-production.sh
# 本番環境用の設定でデプロイ
```

## 🛠️ 開発・テスト

### Docker環境
```bash
./quick-start.sh      # 開発環境を即座に起動
./setup-dev.sh        # 開発環境の設定
./test-setup.sh       # 環境診断
```

### OAuth設定
```bash
./setup-oauth.sh
# オプション1: 本番用認証
# オプション2: 開発用モック認証
```

## 🔒 運用・保守

### セキュリティ
```bash
./harden-security.sh  # セキュリティ強化
```

### モニタリング
```bash
./monitor.sh          # ヘルスチェック開始
./monitor.sh --daemon # バックグラウンドで監視
```

### バックアップ
```bash
./backup.sh           # バックアップ作成
./restore.sh backup.tar.gz  # リストア
```

## 📦 必要なもの

### ローカル実行
- Python 3.7以上
- 5分の時間

### クラウドデプロイ
- GitHubアカウント（推奨）
- 無料アカウント（Replit/Render/Railway）

### 本番環境
- VPSサーバー
- ドメイン（your-domain.com）
- Docker

## 🆘 困ったら

1. **最初に試す**: `python3 run-local-simple.py`
2. **ログを見る**: 各スクリプトの出力を確認
3. **診断する**: `./test-setup.sh`
4. **ドキュメント**: `START_HERE.md`を読む

---

**最速で動かす方法**: 
```bash
python3 run-local-simple.py
```
これだけ！ 🎉