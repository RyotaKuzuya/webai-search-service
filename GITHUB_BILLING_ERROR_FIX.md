# GitHub Actions 課金エラーの解決方法

## エラー内容
```
The job was not started because recent account payments have failed or your spending limit needs to be increased.
```

## 原因
- GitHubアカウントの支払い設定に問題がある
- GitHub Actionsの使用制限に達している
- Claude Max PlanのOAuth認証とは無関係

## 解決方法

### 1. GitHub課金設定の確認
1. https://github.com/settings/billing
2. 支払い方法が有効か確認
3. 使用制限（Spending limit）を確認

### 2. 無料枠の確認
- **Public リポジトリ**: 無制限
- **Private リポジトリ**: 月2,000分まで無料

現在のリポジトリ: **Private** (課金対象)

### 3. 即座の解決策

#### オプション1: リポジトリをPublicにする
```bash
# GitHubでリポジトリ設定を変更
# Settings → General → Danger Zone → Change visibility → Make public
```

#### オプション2: Self-hosted runnerを使用
```yaml
runs-on: self-hosted  # ubuntu-latest の代わりに
```

#### オプション3: ローカル実行に切り替える
```bash
# 既存のローカル実行スクリプトを使用
./claude_local_executor.sh
```

## 推奨される対応

### 短期的解決
1. **リポジトリをPublicに変更**（無料でActions使用可能）
2. **ローカル実行スクリプトの活用**

### 長期的解決
1. GitHub有料プランへのアップグレード
2. Self-hosted runner の設定
3. 別のCI/CDサービスの検討

## Claude Max Plan OAuth認証の状態

**OAuth認証自体は問題ありません。**
- CLAUDE_CODE_OAUTH_TOKEN ✓ 設定済み
- 認証期限切れではない
- GitHub Actionsの実行環境の問題

## 次のステップ

1. リポジトリの可視性を確認:
   https://github.com/RyotaKuzuya/webai-search-service/settings

2. Publicに変更する場合の注意:
   - センシティブな情報が含まれていないか確認
   - .envファイルなどは.gitignoreに含まれているか確認

3. ローカル実行の活用:
   ```bash
   ./claude_local_executor.sh
   ```