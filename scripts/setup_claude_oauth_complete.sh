#!/bin/bash

echo "🔐 Claude OAuth トークン完全セットアップガイド"
echo "=============================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}ステップ1: 現在のClaude Codeバージョン確認${NC}"
claude --version
echo ""

echo -e "${BLUE}ステップ2: 新しいOAuthトークンを生成${NC}"
echo ""
echo "以下のコマンドを実行してください："
echo -e "${GREEN}claude setup-token${NC}"
echo ""
echo "手順："
echo "1. 表示されるURLをブラウザで開く"
echo "2. Anthropicアカウントでログイン"
echo "3. 認証を承認"
echo "4. 表示される認証コードをコピー"
echo "5. ターミナルに貼り付けてEnter"
echo ""
echo -e "${YELLOW}準備ができたらEnterを押してください...${NC}"
read

# トークン生成
echo -e "${BLUE}トークンを生成中...${NC}"
claude setup-token

echo ""
echo -e "${GREEN}✅ トークン生成完了${NC}"
echo ""

echo -e "${BLUE}ステップ3: 生成されたトークンを確認${NC}"
echo ""
echo "トークンの場所: ~/.config/claude/claude_config.json"
echo ""

# トークンを取得
if [ -f "$HOME/.config/claude/claude_config.json" ]; then
    TOKEN=$(cat "$HOME/.config/claude/claude_config.json" | jq -r '.oauth_token // empty' 2>/dev/null)
    
    if [ -n "$TOKEN" ]; then
        echo -e "${GREEN}✅ トークンが見つかりました${NC}"
        echo "トークンの最初の10文字: ${TOKEN:0:10}..."
        echo ""
        
        echo -e "${BLUE}ステップ4: GitHub Secretsを更新${NC}"
        echo ""
        echo "1. 以下のURLにアクセス："
        echo "   https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
        echo ""
        echo "2. CLAUDE_CODE_OAUTH_TOKEN を探す"
        echo ""
        echo "3. 'Update' をクリック（または新規作成）"
        echo ""
        echo "4. Value欄に以下のトークンを貼り付け："
        echo ""
        echo -e "${YELLOW}=== トークン（コピー用） ===${NC}"
        echo "$TOKEN"
        echo -e "${YELLOW}=== ここまで ===${NC}"
        echo ""
        echo "5. 'Update secret' をクリック"
        echo ""
        
        echo -e "${YELLOW}GitHub Secretsを更新しましたか？ (y/n)${NC}"
        read -r response
        
        if [[ "$response" == "y" ]]; then
            echo ""
            echo -e "${GREEN}✅ 素晴らしい！セットアップ完了です${NC}"
            echo ""
            echo -e "${BLUE}ステップ5: 動作テスト${NC}"
            echo ""
            echo "新しいIssueでテスト:"
            echo "1. https://github.com/RyotaKuzuya/webai-search-service/issues/new"
            echo ""
            echo "2. タイトル: OAuth Token Test"
            echo ""
            echo "3. 本文: Testing new OAuth token"
            echo ""
            echo "4. Issueを作成後、コメント："
            echo "   @claude"
            echo "   新しいOAuthトークンでのテストです。応答してください。"
            echo ""
            echo -e "${GREEN}🎉 セットアップ完了！${NC}"
        else
            echo ""
            echo "GitHub Secretsを更新してから、再度テストしてください"
        fi
    else
        echo -e "${RED}❌ トークンの取得に失敗しました${NC}"
        echo "手動で確認してください: cat ~/.config/claude/claude_config.json"
    fi
else
    echo -e "${RED}❌ 設定ファイルが見つかりません${NC}"
    echo "'claude setup-token' を実行してください"
fi