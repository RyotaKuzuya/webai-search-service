# 🎉 朗報：Claude Max Plan が GitHub Actions でサポートされました！

## 📅 最新情報（5日前）

Anthropic開発者（ashwin-ant）からの公式発表：

> "We've added support using this GitHub action with Claude Max. If you update Claude Code to 1.0.44, then /install-github-app command will walk you through the setup."

**Claude Code 1.0.44 以降で Max Plan が使用可能になりました！**

## 🚀 セットアップ手順

### 1. Claude Code を最新版にアップデート
```bash
# Claude Code のバージョン確認
claude --version

# 1.0.44以降でない場合は更新
curl -fsSL https://cli.claude.ai/install.sh | sh
```

### 2. GitHub App をインストール
```bash
# Claude Code内で実行
claude
/install-github-app
```

### 3. OAuthトークンを生成（代替方法）
```bash
# 手動でトークン生成
claude setup-token
```

### 4. GitHub Secretsに設定
- Name: `CLAUDE_CODE_OAUTH_TOKEN`
- Value: 生成されたトークン

### 5. ワークフローを復活
```yaml
name: Claude Code Actions

on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  claude-code:
    runs-on: ubuntu-latest
    if: contains(github.event.comment.body, '@claude')
    
    steps:
      - uses: anthropics/claude-code-action@main
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## ⚠️ 重要な注意

> "Claude Max subscriptions are intended for a single user"

- Max Planは個人利用向け
- 複数ユーザーのリポジトリにはAPIキー推奨

## ✅ つまり

**Max Plan で GitHub Actions が無料で使えるようになりました！**

1. Claude Code を 1.0.44 以降に更新
2. OAuthトークンで認証
3. GitHub Actions 無料（Publicリポジトリ）
4. Claude API 無料（Max Plan）

## 🎊 結論

当初の期待通り、Max Plan で完全無料の GitHub Actions + Claude AI が実現可能になりました！