# Claude Max OAuth トークン取得 クイックガイド

## 🚀 最速セットアップ手順

### ステップ1: トークン生成

ローカルマシンで以下を実行:

```bash
# Claude CLIインストール（未インストールの場合）
curl -fsSL https://cli.claude.ai/install.sh | sh

# OAuth認証
claude auth
```

### ステップ2: トークン取得

認証完了後:

```bash
# トークンを表示
cat ~/.config/claude/claude_config.json | jq -r '.oauth_token'

# またはファイル全体を確認
cat ~/.config/claude/claude_config.json
```

### ステップ3: GitHub Secretsに追加

1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions
2. **New repository secret**
3. 入力:
   - Name: `CLAUDE_CODE_OAUTH_TOKEN`
   - Value: [取得したトークン]

## ⚠️ 重要な注意

- **APIキー方式は使用しない**: Claude Max PlanはOAuth認証のみ対応
- **トークンは安全に管理**: 画面に表示されたトークンは速やかにコピー

## 🔧 確認方法

GitHubで以下を確認:
- Settings → Secrets → `CLAUDE_CODE_OAUTH_TOKEN` が存在すること
- Actions → ワークフローが成功すること

## 📝 参考

公式ドキュメント: https://github.com/anthropics/claude-code-action#authentication