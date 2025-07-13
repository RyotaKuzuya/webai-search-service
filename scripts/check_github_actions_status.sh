#!/bin/bash

echo "🔍 GitHub Actions ステータス確認"
echo "=================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# リポジトリ情報
OWNER="RyotaKuzuya"
REPO="webai-search-service"

echo -e "${BLUE}最近のワークフロー実行状況:${NC}"
echo ""

# GitHub CLIがインストールされているか確認
if command -v gh &> /dev/null; then
    # 最近のワークフロー実行を表示
    gh run list --repo "$OWNER/$REPO" --limit 10
    
    echo ""
    echo -e "${YELLOW}失敗したワークフローの詳細を確認しますか？ (y/n)${NC}"
    read -r response
    
    if [[ "$response" == "y" ]]; then
        # 最新の失敗したワークフローを取得
        FAILED_RUN=$(gh run list --repo "$OWNER/$REPO" --status failure --limit 1 --json databaseId -q '.[0].databaseId')
        
        if [ -n "$FAILED_RUN" ]; then
            echo ""
            echo -e "${RED}失敗したワークフローの詳細:${NC}"
            gh run view "$FAILED_RUN" --repo "$OWNER/$REPO"
            
            echo ""
            echo -e "${YELLOW}ログを確認しますか？ (y/n)${NC}"
            read -r log_response
            
            if [[ "$log_response" == "y" ]]; then
                gh run view "$FAILED_RUN" --repo "$OWNER/$REPO" --log
            fi
        else
            echo -e "${GREEN}最近失敗したワークフローはありません${NC}"
        fi
    fi
else
    echo -e "${RED}GitHub CLIがインストールされていません${NC}"
    echo ""
    echo "以下のURLで手動確認してください:"
    echo "https://github.com/$OWNER/$REPO/actions"
fi

echo ""
echo -e "${BLUE}設定確認チェックリスト:${NC}"
echo ""
echo "✅ Secrets設定を確認:"
echo "   https://github.com/$OWNER/$REPO/settings/secrets/actions"
echo ""
echo "   必要なSecrets:"
echo "   - CLAUDE_CODE_OAUTH_TOKEN ✓ (設定済み)"
echo "   - GITHUB_TOKEN (自動提供)"
echo ""
echo "✅ ワークフロー設定:"
echo "   - claude-code-actions.yml"
echo "   - ai-auto-improvement.yml"
echo "   - continuous-monitoring.yml"
echo ""
echo -e "${GREEN}トラブルシューティング:${NC}"
echo ""
echo "1. もしCLAUDE_CODE_OAUTH_TOKENが期限切れの場合:"
echo "   - ローカルで 'claude auth' を再実行"
echo "   - 新しいトークンでSecretを更新"
echo ""
echo "2. ワークフローが見つからないエラーの場合:"
echo "   - ブランチがmasterであることを確認"
echo "   - .github/workflows/にファイルが存在することを確認"