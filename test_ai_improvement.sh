#!/bin/bash
# AI自動改善システムのテスト

echo "🧪 AI自動改善システム テスト"
echo "=============================="
echo ""

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# リポジトリ情報
OWNER="RyotaKuzuya"
REPO="webai-search-service"

echo -e "${BLUE}テストシナリオを選択してください:${NC}"
echo ""
echo "1. 手動でテストIssueを作成（@claudeメンション付き）"
echo "2. ワークフローを手動実行"
echo "3. 両方実行"
echo ""
echo -n "選択 (1-3): "
read -r choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}テストIssueを作成します${NC}"
        echo ""
        
        # Issue本文
        ISSUE_BODY=$(cat << 'EOF'
@claude 

以下のテストタスクを実行してください：

1. **現在のコードベースの分析**
   - simple_api.py, simple_app.py, claude_simple_session_api.pyの構造分析
   - 潜在的な問題点の特定

2. **改善提案**
   - エラーハンドリングの強化
   - パフォーマンスの最適化
   - コード品質の向上

3. **小さな改善の実装**
   - 適切なログレベルの設定
   - タイムアウト設定の最適化
   - エラーメッセージの改善

このタスクは、AI自動改善システムのテストです。実際の改善を行い、PRを作成してください。
EOF
)
        
        # GitHub CLIでIssue作成
        if command -v gh &> /dev/null; then
            gh issue create \
                --repo "$OWNER/$REPO" \
                --title "🧪 AI自動改善システム テスト" \
                --body "$ISSUE_BODY" \
                --label "ai-improvement,priority:high"
            
            echo -e "${GREEN}テストIssueを作成しました！${NC}"
        else
            echo -e "${YELLOW}GitHub CLIがインストールされていません${NC}"
            echo "以下のURLから手動でIssueを作成してください："
            echo "https://github.com/$OWNER/$REPO/issues/new"
            echo ""
            echo "タイトル: 🧪 AI自動改善システム テスト"
            echo "本文:"
            echo "$ISSUE_BODY"
        fi
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}AI Auto Test & Improvementワークフローを手動実行します${NC}"
        echo ""
        
        if command -v gh &> /dev/null; then
            echo "テストタイプを選択:"
            echo "1. full (全体テスト)"
            echo "2. security (セキュリティテスト)"
            echo "3. performance (パフォーマンステスト)"
            echo "4. usability (使いやすさテスト)"
            echo "5. code-quality (コード品質)"
            echo -n "選択 (1-5): "
            read -r test_type_choice
            
            case $test_type_choice in
                1) TEST_TYPE="full" ;;
                2) TEST_TYPE="security" ;;
                3) TEST_TYPE="performance" ;;
                4) TEST_TYPE="usability" ;;
                5) TEST_TYPE="code-quality" ;;
                *) TEST_TYPE="full" ;;
            esac
            
            gh workflow run "AI Auto Test & Improvement" \
                --repo "$OWNER/$REPO" \
                -f test_type="$TEST_TYPE"
            
            echo -e "${GREEN}ワークフローを開始しました！${NC}"
            echo ""
            echo "進捗を確認: https://github.com/$OWNER/$REPO/actions"
        else
            echo "GitHub CLIがインストールされていません"
            echo "以下のURLから手動で実行してください："
            echo "https://github.com/$OWNER/$REPO/actions/workflows/ai-auto-improvement.yml"
        fi
        ;;
        
    3)
        # 両方実行
        $0 <<< "1"
        echo ""
        $0 <<< "2"
        ;;
        
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}モニタリング:${NC}"
echo ""
echo "1. GitHub Actions: https://github.com/$OWNER/$REPO/actions"
echo "2. Issues: https://github.com/$OWNER/$REPO/issues"
echo "3. Pull Requests: https://github.com/$OWNER/$REPO/pulls"
echo ""
echo -e "${GREEN}テストが開始されました！${NC}"