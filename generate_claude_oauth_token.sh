#!/bin/bash

echo "🔑 Claude Max Plan OAuth Token 生成"
echo "===================================="
echo ""
echo "Claude Max PlanのOAuthトークンを生成します。"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}重要: このスクリプトは対話的な操作が必要です${NC}"
echo ""

# Claude CLIがインストールされているか確認
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}Claude CLIがインストールされていません。インストールしますか？ (y/n)${NC}"
    read -r response
    
    if [[ "$response" == "y" ]]; then
        echo "Claude CLIをインストール中..."
        curl -fsSL https://cli.claude.ai/install.sh | sh
    else
        echo "Claude CLIのインストールをスキップしました"
        exit 1
    fi
fi

echo -e "${GREEN}Claude CLIが見つかりました${NC}"
echo ""

# 既存の認証情報を確認
if [ -f "$HOME/.config/claude/claude_config.json" ]; then
    echo -e "${YELLOW}既存の認証情報が見つかりました${NC}"
    echo "新しいトークンを生成しますか？ (y/n)"
    read -r response
    
    if [[ "$response" != "y" ]]; then
        echo "既存のトークンを使用します"
        
        # 既存のトークンを表示
        echo ""
        echo -e "${BLUE}既存のトークン情報:${NC}"
        cat "$HOME/.config/claude/claude_config.json" | jq -r '.oauth_token // empty' 2>/dev/null || echo "トークンの読み取りに失敗しました"
        exit 0
    fi
fi

echo -e "${BLUE}新しいOAuthトークンを生成します${NC}"
echo ""
echo "以下のコマンドを実行してください："
echo ""
echo -e "${GREEN}claude auth${NC}"
echo ""
echo "認証が完了したら、生成されたトークンをGitHub Secretsに追加してください。"
echo ""

# 認証を実行
echo "今すぐ認証を開始しますか？ (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    claude auth
    
    # 認証成功後、トークンを取得して表示
    if [ -f "$HOME/.config/claude/claude_config.json" ]; then
        echo ""
        echo -e "${GREEN}認証が完了しました！${NC}"
        echo ""
        
        # トークン情報を取得
        ACCESS_TOKEN=$(cat "$HOME/.config/claude/claude_config.json" | jq -r '.oauth_token // empty' 2>/dev/null)
        
        if [ -n "$ACCESS_TOKEN" ]; then
            echo -e "${BLUE}GitHub Secretsに以下を追加してください:${NC}"
            echo ""
            echo "1. リポジトリの Settings > Secrets and variables > Actions"
            echo "2. 'New repository secret' をクリック"
            echo "3. 以下の情報を入力:"
            echo ""
            echo "   Name: CLAUDE_CODE_OAUTH_TOKEN"
            echo "   Value: [生成されたトークン]"
            echo ""
            echo -e "${YELLOW}セキュリティのため、トークンは画面に表示しません${NC}"
            echo "トークンは ~/.config/claude/claude_config.json に保存されています"
        else
            echo -e "${YELLOW}トークンの取得に失敗しました${NC}"
        fi
    fi
else
    echo "認証をスキップしました"
    echo "後で 'claude auth' コマンドを実行してください"
fi

echo ""
echo -e "${BLUE}ワークフローの更新方法:${NC}"
echo ""
cat << 'EOF'
# .github/workflows/claude-code-actions.yml を以下のように更新:

name: Claude Code Actions

on:
  issue_comment:
    types: [created]
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  claude-code:
    runs-on: ubuntu-latest
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      github.event_name == 'pull_request'
    
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
EOF

echo ""
echo -e "${GREEN}設定が完了したら、ワークフローが正常に動作するはずです！${NC}"