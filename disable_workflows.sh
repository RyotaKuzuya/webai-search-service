#!/bin/bash
# GitHub Actionsの実行中のワークフローを停止

echo "🛑 GitHub Actions ワークフロー無効化スクリプト"
echo "==========================================="
echo ""

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}注意: このスクリプトはGitHub CLIが必要です${NC}"
echo ""

# GitHub CLIの確認
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) がインストールされていません${NC}"
    echo "インストール方法:"
    echo "  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "  echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null"
    echo "  sudo apt update"
    echo "  sudo apt install gh"
    exit 1
fi

# 認証確認
if ! gh auth status &> /dev/null; then
    echo -e "${RED}GitHub CLIの認証が必要です${NC}"
    echo "実行: gh auth login"
    exit 1
fi

echo -e "${GREEN}GitHub CLIの準備ができています${NC}"
echo ""

# リポジトリ情報
OWNER="RyotaKuzuya"
REPO="webai-search-service"

echo "リポジトリ: $OWNER/$REPO"
echo ""

# 実行中のワークフローを確認
echo "実行中のワークフローを確認中..."
echo ""

# 実行中のワークフローを取得
runs=$(gh run list --repo "$OWNER/$REPO" --status in_progress --json databaseId,name,status --limit 20)

if [ -z "$runs" ] || [ "$runs" = "[]" ]; then
    echo -e "${GREEN}実行中のワークフローはありません${NC}"
else
    echo -e "${YELLOW}実行中のワークフロー:${NC}"
    echo "$runs" | jq -r '.[] | "\(.databaseId) - \(.name)"'
    echo ""
    
    # 停止確認
    read -p "これらのワークフローを停止しますか？ (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo ""
        echo "ワークフローを停止中..."
        
        # 各ワークフローを停止
        echo "$runs" | jq -r '.[].databaseId' | while read -r run_id; do
            echo "停止: $run_id"
            gh run cancel "$run_id" --repo "$OWNER/$REPO" || echo "エラー: $run_id の停止に失敗"
        done
        
        echo ""
        echo -e "${GREEN}ワークフローの停止が完了しました${NC}"
    else
        echo -e "${YELLOW}停止をキャンセルしました${NC}"
    fi
fi

echo ""
echo "📝 今後の推奨事項:"
echo ""
echo "1. ローカルでClaude Codeを実行:"
echo "   ./claude_local_executor.sh"
echo ""
echo "2. 手動でサービスを管理:"
echo "   ./start_services.sh"
echo ""
echo "3. Gitプッシュ時の自動実行を無効化済み"
echo ""
echo -e "${GREEN}完了！${NC}"