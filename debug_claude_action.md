# Claude Code Action デバッグガイド

## 現在の状況
- Issue #3 で @claude メンションしたが反応なし
- ワークフローの構文は正しい
- OAuth トークンは設定済み

## 考えられる原因

### 1. アクションが存在しない可能性
`anthropics/claude-code-action` が実際に存在するか確認が必要

### 2. OAuth トークンの形式
CLAUDE_CODE_OAUTH_TOKEN が正しい形式か確認

### 3. ワークフローが実行されていない
GitHub Actions タブで実行履歴を確認：
https://github.com/RyotaKuzuya/webai-search-service/actions

## デバッグ手順

### ステップ 1: Actions実行履歴を確認
1. https://github.com/RyotaKuzuya/webai-search-service/actions
2. ワークフローが実行されているか確認
3. エラーメッセージを確認

### ステップ 2: シンプルなテストワークフローを作成
```yaml
name: Debug Test

on:
  issue_comment:
    types: [created]

jobs:
  debug:
    runs-on: ubuntu-latest
    if: contains(github.event.comment.body, '@test')
    steps:
      - name: Echo test
        run: |
          echo "Comment detected!"
          echo "Issue number: ${{ github.event.issue.number }}"
          echo "Comment: ${{ github.event.comment.body }}"
```

### ステップ 3: 公式アクションの確認
1. https://github.com/anthropics/claude-code-action が存在するか確認
2. 存在しない場合は、別のアクション名の可能性

### ステップ 4: 代替案
もしclaude-code-actionが使えない場合：
1. 自作のワークフローでClaude APIを直接呼び出す
2. ローカル実行スクリプトを使用する