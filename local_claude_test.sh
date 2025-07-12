#!/bin/bash

echo "🤖 Claude ローカルテスト実行"
echo "=============================="
echo ""
echo "GitHub Actionsの課金制限を回避してローカルでテストします"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Claude CLIの確認
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}Claude CLIがインストールされていません${NC}"
    echo "インストール方法:"
    echo "curl -fsSL https://cli.claude.ai/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}Claude CLIが見つかりました${NC}"
echo ""

# テストオプション
echo -e "${BLUE}テストを選択してください:${NC}"
echo ""
echo "1. 簡単な動作確認"
echo "2. コード分析（simple_api.py）"
echo "3. AI自動改善シミュレーション"
echo "4. カスタムプロンプト"
echo ""
echo -n "選択 (1-4): "
read -r choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}簡単な動作確認を実行${NC}"
        claude "こんにちは！正常に動作しているか確認のため、簡単に応答してください。"
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}コード分析を実行${NC}"
        claude "simple_api.pyのコードを確認して、以下の点について簡単にコメントしてください：
1. エラーハンドリングは適切か
2. 改善できる点はあるか
簡潔な回答で構いません。" --model sonnet-3.5
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}AI自動改善シミュレーション${NC}"
        claude "以下のテストタスクを実行してください：

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

実際のコード改善案を提示してください。" --model sonnet-3.5
        ;;
        
    4)
        echo ""
        echo -e "${BLUE}カスタムプロンプトを入力してください:${NC}"
        read -r custom_prompt
        claude "$custom_prompt" --model sonnet-3.5
        ;;
        
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}テスト完了！${NC}"
echo ""
echo -e "${YELLOW}注意: これはローカル実行のため、GitHubへの自動反映はされません${NC}"
echo ""
echo "GitHub Actionsを使用したい場合の選択肢:"
echo "1. リポジトリをPublicに変更"
echo "2. GitHubの支払い設定を更新"
echo "3. Self-hosted runnerを設定"