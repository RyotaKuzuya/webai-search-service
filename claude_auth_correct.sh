#!/bin/bash

echo "🔐 Claude Code 正しい認証方法"
echo "============================"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}重要な発見：${NC}"
echo "auth.claude.ai は Claude Code CLI 専用の内部エンドポイントです"
echo "ブラウザから直接アクセスすることはできません"
echo ""

echo -e "${GREEN}正しい認証方法：${NC}"
echo ""

echo -e "${YELLOW}方法1: Claude CLIを使用（推奨）${NC}"
echo "1. Claude CLIがインストールされているか確認:"
echo "   claude --version"
echo ""
echo "2. 認証コマンドを実行:"
echo "   claude auth"
echo ""
echo "3. 表示されるURLをブラウザで開く"
echo "   （このURLは claude.ai ドメインになります）"
echo ""
echo "4. Anthropicアカウントでログイン"
echo ""
echo "5. 認証コードをターミナルに貼り付け"
echo ""

echo -e "${YELLOW}方法2: トークン生成コマンド${NC}"
echo "claude setup-token"
echo ""
echo "このコマンドも同様の流れで認証を行います"
echo ""

echo -e "${BLUE}トークン取得後の確認：${NC}"
echo "cat ~/.config/claude/claude_config.json | jq -r '.oauth_token'"
echo ""

echo -e "${RED}注意事項：${NC}"
echo "- auth.claude.ai はCLI内部でのみ使用されます"
echo "- ブラウザで直接開くことはできません"
echo "- 必ずCLIコマンドから認証を開始してください"
echo ""

echo -e "${GREEN}次のステップ：${NC}"
echo "1. 上記のいずれかのコマンドを実行"
echo "2. 生成されたトークンをGitHub Secretsに登録"
echo "3. @claude メンションでテスト"