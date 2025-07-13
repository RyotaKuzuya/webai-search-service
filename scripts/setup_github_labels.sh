#!/bin/bash
# GitHub Issue用のラベルセットアップ

echo "🏷️  GitHub Labels セットアップ"
echo "============================="
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
    ["priority:high"]="FF0000"
    ["priority:middle"]="FFA500"
    ["priority:low"]="FFFF00"
    ["claude-processed"]="0E8A16"
    ["claude-code-requested"]="1D76DB"
    ["bug"]="D73A4A"
    ["enhancement"]="A2EEEF"
    ["documentation"]="0075CA"
    ["security"]="FF0000"
    ["performance"]="7057FF"
)

echo "以下のラベルを作成します："
for label in "${!labels[@]}"; do
    echo "  - $label (色: #${labels[$label]})"
done

echo ""
echo -e "${YELLOW}注意: GitHub CLIまたはWeb UIでラベルを作成してください${NC}"
echo ""

# GitHub CLIを使う場合のコマンド
echo "GitHub CLIでの作成コマンド:"
echo ""
for label in "${!labels[@]}"; do
    echo "gh label create \"$label\" --repo \"$OWNER/$REPO\" --color \"${labels[$label]}\""
done

echo ""
echo "または、以下のURLで手動作成:"
echo "https://github.com/$OWNER/$REPO/labels"
echo ""

# 使用例
echo -e "${BLUE}使用例:${NC}"
echo ""
echo "1. 高優先度のバグ報告:"
echo "   - Title: '🐛 ログイン機能が動作しない'"
echo "   - Labels: 'bug', 'priority:high'"
echo ""
echo "2. 中優先度の機能追加:"
echo "   - Title: '✨ ダークモードの追加'"
echo "   - Labels: 'enhancement', 'priority:middle'"
echo ""
echo "3. 低優先度のドキュメント更新:"
echo "   - Title: '📝 READMEの更新'"
echo "   - Labels: 'documentation', 'priority:low'"
echo ""
echo "夜間に自動的にClaudeがこれらのIssueを処理します！"