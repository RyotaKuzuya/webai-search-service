#!/bin/bash
# GitHub Actions課金制限をバイパスしてClaude Maxで実行

echo "🚀 Claude Max GitHub Actions Bypass"
echo "=================================="
echo ""
echo "GitHub課金制限を回避してClaude Codeを実行します"
echo ""

# 実行するタスクを選択
echo "実行するタスクを選択してください："
echo "1) コードレビュー"
echo "2) 定期メンテナンス"
echo "3) バグ修正"
echo "4) カスタムタスク"
echo ""
read -p "選択 (1-4): " choice

case $choice in
    1)
        echo "📝 コードレビューを実行中..."
        cd /home/ubuntu/webai
        claude "WebAIプロジェクトのコードレビューをしてください。simple_api.pyとsimple_app.pyを中心に、セキュリティ、パフォーマンス、コード品質の観点から確認してください。" --thinking
        ;;
    2)
        echo "🔧 定期メンテナンスを実行中..."
        cd /home/ubuntu/webai
        claude "WebAIプロジェクトの定期メンテナンスを実行してください。依存関係の更新、セキュリティパッチ、改善提案を含めてください。" --thinking
        ;;
    3)
        echo "🐛 バグ修正を実行中..."
        cd /home/ubuntu/webai
        claude "WebAIプロジェクトの既知のバグや問題を調査し、修正してください。エラーログも確認してください。" --thinking
        ;;
    4)
        echo "カスタムタスクを入力してください："
        read -p "> " custom_task
        cd /home/ubuntu/webai
        claude "$custom_task" --thinking
        ;;
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "✅ タスク完了!"
echo ""
echo "結果は画面に表示されました。"
echo "必要に応じて、変更をコミット・プッシュしてください。"