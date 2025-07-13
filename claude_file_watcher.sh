#!/bin/bash

echo "🔍 Claude File Watcher - GitHub Actions不要の自動化"
echo "=================================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 監視対象ファイル
WATCH_FILES=(
    "simple_api.py"
    "simple_app.py"
    "claude_simple_session_api.py"
    "templates/*.html"
)

# 最後のチェック時刻
LAST_CHECK=$(date +%s)

echo -e "${BLUE}監視対象ファイル:${NC}"
for file in "${WATCH_FILES[@]}"; do
    echo "  - $file"
done
echo ""

echo -e "${GREEN}監視を開始します...${NC}"
echo "Ctrl+C で終了"
echo ""

while true; do
    # 変更されたファイルをチェック
    CHANGED_FILES=""
    
    for pattern in "${WATCH_FILES[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                # ファイルの最終更新時刻を取得
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    FILE_TIME=$(stat -f %m "$file")
                else
                    FILE_TIME=$(stat -c %Y "$file")
                fi
                
                if [ "$FILE_TIME" -gt "$LAST_CHECK" ]; then
                    CHANGED_FILES="$CHANGED_FILES $file"
                fi
            fi
        done
    done
    
    # 変更があった場合
    if [ -n "$CHANGED_FILES" ]; then
        echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] 変更を検出:${NC}"
        echo "$CHANGED_FILES"
        echo ""
        
        # Claudeでレビュー
        echo -e "${BLUE}Claudeでコードレビュー中...${NC}"
        
        for file in $CHANGED_FILES; do
            echo -e "${GREEN}レビュー: $file${NC}"
            
            # ファイルの内容をClaudeに送信
            claude "以下のファイルの変更をレビューしてください。改善点があれば指摘してください: $(cat "$file")" \
                --model sonnet-3.5 \
                --max-tokens 1000
            
            echo ""
            echo "---"
            echo ""
        done
        
        # 最後のチェック時刻を更新
        LAST_CHECK=$(date +%s)
    fi
    
    # 30秒待機
    sleep 30
done