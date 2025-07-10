#!/bin/bash
# Claude Local Executor - GitHub Actions代替スクリプト

echo "🚀 Claude Local Executor"
echo "======================="
echo ""
echo "GitHub Actionsの課金制限を回避してClaude Codeを実行します"
echo ""

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# メニュー表示
show_menu() {
    echo -e "${BLUE}実行するタスクを選択してください:${NC}"
    echo ""
    echo "1) 📝 コードレビュー"
    echo "2) 🐛 バグ修正"
    echo "3) ⚡ パフォーマンス最適化"
    echo "4) 🔒 セキュリティチェック"
    echo "5) 📦 依存関係の更新"
    echo "6) 🎯 カスタムタスク"
    echo "7) 🔄 最近の変更をレビュー"
    echo "8) 📊 プロジェクト分析"
    echo "9) 🧪 テスト追加"
    echo "0) 終了"
    echo ""
}

# モデル選択
select_model() {
    echo -e "${BLUE}使用するモデルを選択してください:${NC}"
    echo "1) Claude Sonnet 4 (推奨)"
    echo "2) Claude Opus 4"
    echo "3) Claude 3.5 Sonnet"
    echo "4) Claude 3.5 Haiku"
    read -p "選択 (1-4) [1]: " model_choice
    
    case ${model_choice:-1} in
        1) MODEL="sonnet4" ;;
        2) MODEL="opus4" ;;
        3) MODEL="sonnet" ;;
        4) MODEL="haiku" ;;
        *) MODEL="sonnet4" ;;
    esac
    
    echo -e "${GREEN}選択されたモデル: $MODEL${NC}"
}

# タスク実行
execute_task() {
    local task_type=$1
    local prompt=""
    
    case $task_type in
        1)
            prompt="WebAIプロジェクトのコードレビューを実行してください。以下の観点でチェック：1. セキュリティの問題 2. パフォーマンスの改善点 3. コード品質 4. ベストプラクティスの遵守。simple_api.py, simple_app.py, claude_simple_session_api.pyを重点的に確認してください。"
            ;;
        2)
            prompt="WebAIプロジェクトの既知のバグや問題を調査し、修正してください。エラーログも確認し、潜在的な問題も特定してください。"
            ;;
        3)
            prompt="WebAIプロジェクトのパフォーマンスを最適化してください。1. レスポンス時間の改善 2. リソース使用量の削減 3. 並行処理の最適化"
            ;;
        4)
            prompt="WebAIプロジェクトのセキュリティ監査を実行してください。1. SQLインジェクション対策 2. XSS対策 3. 認証・認可の確認 4. セキュアな設定の確認"
            ;;
        5)
            prompt="requirements.txtの依存関係を確認し、必要に応じて更新してください。セキュリティアップデートを優先してください。"
            ;;
        6)
            echo "カスタムタスクを入力してください："
            read -p "> " prompt
            ;;
        7)
            # 最近の変更を取得
            echo -e "${YELLOW}最近の変更を確認中...${NC}"
            git log --oneline -10
            prompt="最近のコミットによる変更をレビューし、改善点や潜在的な問題を指摘してください。"
            ;;
        8)
            prompt="WebAIプロジェクト全体を分析し、アーキテクチャの改善提案、技術的負債の特定、今後の開発方針を提案してください。"
            ;;
        9)
            prompt="WebAIプロジェクトのテストカバレッジを確認し、不足しているテストを追加してください。特に重要な機能に対するユニットテストとインテグレーションテストを優先してください。"
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            return 1
            ;;
    esac
    
    # 実行確認
    echo ""
    echo -e "${YELLOW}実行するプロンプト:${NC}"
    echo "$prompt"
    echo ""
    read -p "実行しますか？ (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Claude Codeを実行中...${NC}"
        
        # 思考モードの選択
        echo ""
        echo "思考モードを選択してください："
        echo "1) 通常"
        echo "2) think (4K)"
        echo "3) megathink (10K)"
        echo "4) think harder (20K)"
        read -p "選択 (1-4) [1]: " think_choice
        
        case ${think_choice:-1} in
            2) prompt="think: $prompt" ;;
            3) prompt="megathink: $prompt" ;;
            4) prompt="think harder: $prompt" ;;
        esac
        
        # Claude実行
        cd /home/ubuntu/webai
        claude "$prompt" --model "$MODEL"
        
        # 結果をログに保存
        timestamp=$(date +"%Y%m%d_%H%M%S")
        log_file="claude_results/task_${timestamp}.log"
        mkdir -p claude_results
        echo "タスク実行結果 - $timestamp" > "$log_file"
        echo "プロンプト: $prompt" >> "$log_file"
        echo "モデル: $MODEL" >> "$log_file"
        
        echo -e "${GREEN}タスク完了！${NC}"
        echo "結果は $log_file に保存されました"
    else
        echo -e "${YELLOW}実行をキャンセルしました${NC}"
    fi
}

# メインループ
while true; do
    show_menu
    read -p "選択 (0-9): " choice
    
    if [[ "$choice" == "0" ]]; then
        echo -e "${GREEN}終了します${NC}"
        break
    fi
    
    if [[ "$choice" =~ ^[1-9]$ ]]; then
        select_model
        execute_task "$choice"
        echo ""
        echo "Enterキーを押して続行..."
        read
        clear
    else
        echo -e "${RED}無効な選択です${NC}"
        sleep 1
    fi
done