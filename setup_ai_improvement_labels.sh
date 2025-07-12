#!/bin/bash
# AI自動改善システム用のGitHubラベルセットアップ

echo "🏷️  AI自動改善システム用 GitHub Labels セットアップ"
echo "=================================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# リポジトリ情報
OWNER="RyotaKuzuya"
REPO="webai-search-service"

echo "リポジトリ: $OWNER/$REPO"
echo ""

# 作成するラベル
declare -A labels=(
    ["ai-improvement"]="0E8A16"
    ["priority:high"]="FF0000"
    ["monitoring-alert"]="FF6B6B"
    ["ai-analysis"]="4ECDC4"
    ["full"]="7209B7"
    ["security"]="D90429"
    ["performance"]="F77F00"
    ["usability"]="06FFA5"
    ["code-quality"]="003049"
    ["claude-processed"]="0E8A16"
)

echo "以下のラベルを作成します："
for label in "${!labels[@]}"; do
    echo "  - $label (色: #${labels[$label]})"
done

echo ""
echo -e "${YELLOW}注意: GitHub CLIを使用してラベルを作成します${NC}"
echo ""

# GitHub CLIがインストールされているか確認
if command -v gh &> /dev/null; then
    echo -e "${GREEN}GitHub CLIが見つかりました${NC}"
    echo ""
    
    echo "ラベルを作成しますか？ (y/n)"
    read -r response
    
    if [[ "$response" == "y" ]]; then
        for label in "${!labels[@]}"; do
            echo "作成中: $label"
            gh label create "$label" --repo "$OWNER/$REPO" --color "${labels[$label]}" --force || echo "ラベル '$label' は既に存在するか、作成に失敗しました"
        done
        echo ""
        echo -e "${GREEN}ラベルの作成が完了しました！${NC}"
    else
        echo "ラベル作成をスキップしました"
    fi
else
    echo -e "${RED}GitHub CLIがインストールされていません${NC}"
    echo ""
    echo "GitHub CLIをインストールするか、以下のコマンドを使用してください："
    echo ""
    for label in "${!labels[@]}"; do
        echo "gh label create \"$label\" --repo \"$OWNER/$REPO\" --color \"${labels[$label]}\" --force"
    done
fi

echo ""
echo "または、以下のURLで手動作成:"
echo "https://github.com/$OWNER/$REPO/labels"
echo ""

echo -e "${BLUE}AI自動改善システムの使い方:${NC}"
echo ""
echo "1. 定期実行（毎日深夜2時）:"
echo "   - 自動的にアプリケーションの健全性をチェック"
echo "   - 問題を検出した場合、自動的にIssueを作成"
echo "   - @claudeメンションでClaude Code Actionが起動"
echo ""
echo "2. 手動実行:"
echo "   - GitHub Actions > AI Auto Test & Improvement"
echo "   - 'Run workflow'をクリック"
echo "   - テストタイプを選択（full/security/performance/usability/code-quality）"
echo ""
echo "3. 継続的モニタリング:"
echo "   - 1時間ごとにメトリクスを収集"
echo "   - アラート条件に該当する場合、自動的にIssueを作成"
echo ""
echo -e "${GREEN}セットアップ完了！${NC}"