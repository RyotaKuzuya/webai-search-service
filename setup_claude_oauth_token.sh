#!/bin/bash
# Claude Code OAuth Token Setup for GitHub Actions

echo "🔐 Claude Code OAuth Token セットアップ"
echo "======================================"
echo ""

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}このスクリプトはClaude Code OAuth TokenをGitHub Actionsで使用するために設定します${NC}"
echo ""

# Claude CLIの確認
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Claude CLIがインストールされていません${NC}"
    echo "先にClaude CLIをインストールしてください"
    exit 1
fi

echo -e "${GREEN}Claude CLIが見つかりました${NC}"
echo ""

# 認証状態確認
echo "現在の認証状態を確認中..."
claude_status=$(claude /status 2>&1)

if [[ $claude_status == *"Max Account"* ]]; then
    echo -e "${GREEN}✓ Claude Maxアカウントでログイン済み${NC}"
else
    echo -e "${YELLOW}Claude Maxアカウントでログインが必要です${NC}"
    echo "実行: claude"
    exit 1
fi

echo ""
echo -e "${BLUE}OAuth Tokenを生成します...${NC}"
echo ""

# OAuth Token生成
echo "以下のコマンドを実行してOAuth Tokenを生成してください："
echo ""
echo -e "${YELLOW}claude setup-token${NC}"
echo ""
echo "生成されたトークンが表示されます。"
echo ""

# 手動でトークン生成を促す
read -p "上記コマンドを実行してトークンを生成しましたか？ (y/N): " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "${RED}セットアップをキャンセルしました${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}生成されたOAuth Tokenを入力してください:${NC}"
read -s oauth_token

if [ -z "$oauth_token" ]; then
    echo -e "${RED}トークンが入力されませんでした${NC}"
    exit 1
fi

echo ""
echo ""
echo -e "${GREEN}トークンを受け取りました${NC}"
echo ""

# GitHub Secretsへの追加方法を表示
echo -e "${BLUE}GitHub Secretsへの追加方法:${NC}"
echo ""
echo "1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions"
echo "   にアクセス"
echo ""
echo "2. 'New repository secret' をクリック"
echo ""
echo "3. 以下を入力:"
echo "   Name: CLAUDE_CODE_OAUTH_TOKEN"
echo "   Value: [生成されたトークン]"
echo ""
echo "4. 'Add secret' をクリック"
echo ""

# トークンをファイルに保存（オプション）
echo -e "${YELLOW}トークンをローカルファイルに保存しますか？${NC}"
echo "（セキュリティ上、推奨されません）"
read -p "(y/N): " save_token

if [[ $save_token =~ ^[Yy]$ ]]; then
    echo "$oauth_token" > ~/.claude_oauth_token
    chmod 600 ~/.claude_oauth_token
    echo -e "${GREEN}トークンを ~/.claude_oauth_token に保存しました${NC}"
    echo -e "${RED}注意: このファイルは絶対に共有しないでください${NC}"
fi

echo ""
echo -e "${GREEN}✅ セットアップ手順が完了しました${NC}"
echo ""
echo "次のステップ:"
echo "1. GitHub Secretsにトークンを追加"
echo "2. GitHub Actionsワークフローを実行"
echo ""
echo "使用例:"
echo "- Issue/PRで: @claude コードをレビューしてください"
echo "- 手動実行: Actions → Claude Code Official → Run workflow"
echo ""

# 古いワークフローの置き換えを提案
echo -e "${YELLOW}推奨: 古い無効化されたワークフローを削除して、新しいワークフローを使用してください${NC}"
echo ""
echo "削除対象:"
echo "- claude-code-assistant.yml (DISABLED)"
echo "- claude-webai-maintenance.yml (DISABLED)"
echo "- deploy.yml (DISABLED)"
echo "- optimized-deploy.yml (DISABLED)"
echo ""
echo "新規使用:"
echo "- claude-code-official.yml (公式Action)"
echo "- claude-local-runner.yml (ローカル実行補助)"