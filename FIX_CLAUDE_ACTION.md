# Claude Code Action 修正方法

## 🔍 問題の原因

`startup_failure`の原因が判明しました：

### 必要な手順を実行していない
1. **Claude GitHub App のインストールが必要**
2. URL: https://github.com/apps/claude

## ✅ 解決手順

### 1. Claude GitHub App をインストール
1. https://github.com/apps/claude にアクセス
2. 「Install」をクリック
3. 「RyotaKuzuya/webai-search-service」を選択
4. 権限を確認して承認

### 2. CLAUDE_CODE_OAUTH_TOKEN の確認
- すでに設定済みとのことなので、この手順はスキップ

### 3. 再テスト
- Issue #4 で再度 `@claude` メンション
- または新しいIssueを作成

## 📝 代替案（App インストールが不要な方法）

もしClaude GitHub Appをインストールしたくない場合は、別のアプローチを使用：

### カスタムワークフローを作成
```yaml
name: Custom Claude Integration

on:
  issue_comment:
    types: [created]

jobs:
  claude-response:
    runs-on: ubuntu-latest
    if: contains(github.event.comment.body, '@claude')
    
    steps:
      - name: Setup Claude CLI
        run: |
          curl -fsSL https://cli.claude.ai/install.sh | sh
          
      - name: Process with Claude
        env:
          CLAUDE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # コメント内容を処理
          echo "${{ github.event.comment.body }}" | claude --model sonnet-3.5
```

## 🎯 推奨アクション

1. **最も簡単**: Claude GitHub App をインストール
   - https://github.com/apps/claude
   
2. **すぐに動作確認可能**: インストール後、既存のIssue #4で再テスト

3. **確認URL**:
   - Actions: https://github.com/RyotaKuzuya/webai-search-service/actions
   - Issue: https://github.com/RyotaKuzuya/webai-search-service/issues/4