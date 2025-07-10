#!/bin/bash
# 古いワークフローを削除

echo "🧹 古いワークフローのクリーンアップ"
echo "===================================="
echo ""

cd /home/ubuntu/webai

# 削除対象のワークフロー
OLD_WORKFLOWS=(
    ".github/workflows/claude-code-assistant.yml"
    ".github/workflows/claude-webai-maintenance.yml"
    ".github/workflows/deploy.yml"
    ".github/workflows/optimized-deploy.yml"
)

echo "以下のワークフローを削除します:"
for workflow in "${OLD_WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        echo "  - $workflow"
    fi
done

echo ""
read -p "削除を実行しますか？ (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    for workflow in "${OLD_WORKFLOWS[@]}"; do
        if [ -f "$workflow" ]; then
            rm "$workflow"
            echo "削除: $workflow"
        fi
    done
    
    echo ""
    echo "✅ クリーンアップ完了"
    
    # Gitにコミット
    echo ""
    read -p "変更をGitにコミットしますか？ (y/N): " commit_confirm
    
    if [[ $commit_confirm =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "🧹 古い無効化されたワークフローを削除 - Claude公式Actionに移行"
        git push origin master
        echo "✅ コミット完了"
    fi
else
    echo "キャンセルしました"
fi