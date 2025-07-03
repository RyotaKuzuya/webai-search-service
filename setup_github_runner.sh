#!/bin/bash
# GitHub Actions セルフホストランナーのセットアップスクリプト

set -e

echo "GitHub Actions セルフホストランナーのセットアップを開始します..."

# ランナー用ディレクトリの作成
RUNNER_DIR="/home/ubuntu/actions-runner"
mkdir -p $RUNNER_DIR
cd $RUNNER_DIR

# 最新バージョンのランナーをダウンロード
RUNNER_VERSION="2.317.0"
echo "ランナーバージョン $RUNNER_VERSION をダウンロードしています..."
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
  https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# 展開
echo "ファイルを展開しています..."
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
rm actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo ""
echo "セットアップ準備が完了しました！"
echo ""
echo "次の手順を実行してください："
echo "1. GitHubリポジトリの Settings > Actions > Runners に移動"
echo "2. 'New self-hosted runner' をクリック"
echo "3. 表示されるトークンをコピー"
echo "4. 以下のコマンドを実行："
echo ""
echo "cd $RUNNER_DIR"
echo "./config.sh --url https://github.com/RyotaKuzuya/webai-search-service --token YOUR_TOKEN_HERE"
echo ""
echo "5. 設定完了後、以下でランナーを起動："
echo "./run.sh"
echo ""
echo "または、サービスとして登録："
echo "sudo ./svc.sh install"
echo "sudo ./svc.sh start"