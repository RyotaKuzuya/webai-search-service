#!/bin/bash
# Setup GitHub Self-Hosted Runner for Claude CLI

echo "GitHub Self-Hosted Runner セットアップスクリプト"
echo "=============================================="
echo ""
echo "このスクリプトは、Claude CLIをGitHub Actionsで使用するための"
echo "セルフホステッドランナーをセットアップします。"
echo ""

# Check if Claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo "❌ Claude CLIがインストールされていません。"
    echo "先にClaude CLIをインストールしてください。"
    exit 1
fi

echo "✅ Claude CLIが見つかりました。"

# Create runner directory
RUNNER_DIR="$HOME/github-runner"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download latest runner
RUNNER_VERSION="2.317.0"
echo "GitHub Actions Runnerをダウンロード中..."
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
rm ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo ""
echo "セットアップ手順:"
echo "=================="
echo ""
echo "1. GitHubリポジトリにアクセス:"
echo "   https://github.com/RyotaKuzuya/webai-search-service/settings/actions/runners"
echo ""
echo "2. 'New self-hosted runner' をクリック"
echo ""
echo "3. 表示されたトークンを使用して以下のコマンドを実行:"
echo ""
echo "cd $RUNNER_DIR"
echo "./config.sh --url https://github.com/RyotaKuzuya/webai-search-service --token YOUR_TOKEN"
echo ""
echo "4. ランナーを起動:"
echo "./run.sh"
echo ""
echo "5. バックグラウンドで実行する場合:"
echo "nohup ./run.sh > runner.log 2>&1 &"