# WebAI External HDD Storage Setup

## 概要
WebAIのデータストレージを外付けHDD（150GB）に移行しました。これにより、メインディスクの容量を節約し、大容量のログやデータを保存できるようになりました。

## 外付けHDDの情報
- **デバイス**: `/dev/sdb1`
- **マウントポイント**: `/mnt/external-hdd`
- **ファイルシステム**: ext4
- **容量**: 150GB
- **UUID**: `40d35b00-52b1-492f-8cd3-fed8e57b59da`

## ディレクトリ構造
```
/mnt/external-hdd/webai-data/
├── db/            # データベースファイル
│   └── webai.db
├── logs/          # アプリケーションログ
├── uploads/       # アップロードファイル
├── cache/         # キャッシュファイル
├── backups/       # バックアップファイル
└── claude-home/   # Claude設定とデータ
```

## 設定ファイル
- **config.py**: 外付けHDDのパス設定
- **.env.external-hdd**: 環境変数定義

## シンボリックリンク
互換性のため、以下のシンボリックリンクが作成されています：
- `/home/ubuntu/webai/webai.db` → `/mnt/external-hdd/webai-data/db/webai.db`
- `/home/ubuntu/webai/*.log` → `/mnt/external-hdd/webai-data/logs/*.log`
- `/home/ubuntu/webai/claude-home` → `/mnt/external-hdd/webai-data/claude-home`

## 自動マウント設定
`/etc/fstab`に以下のエントリが追加されています：
```
UUID=40d35b00-52b1-492f-8cd3-fed8e57b59da /mnt/external-hdd ext4 defaults,noatime 0 2
```

## メンテナンス

### ディスク容量確認
```bash
df -h /mnt/external-hdd
```

### データベースバックアップ
```bash
./scripts/backup.sh
```
バックアップは`/mnt/external-hdd/webai-data/backups/`に保存されます。

### ログローテーション
ログファイルは外付けHDDに保存されるため、定期的なクリーンアップを推奨します。

## トラブルシューティング

### 外付けHDDがマウントされない場合
```bash
# 手動マウント
sudo mount /dev/sdb1 /mnt/external-hdd

# またはfstabから再マウント
sudo mount -a
```

### 権限エラーが発生する場合
```bash
sudo chown -R ubuntu:ubuntu /mnt/external-hdd/webai-data
```

## 注意事項
- 外付けHDDを取り外す前に、必ずアプリケーションを停止してください
- 定期的にバックアップを取ることを推奨します
- ディスク容量を定期的に監視してください