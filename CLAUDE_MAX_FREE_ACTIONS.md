# Claude Max Plan で GitHub Actions を無料で使用する方法

## 重要な情報

Zennの記事によると：
> **Claude Proユーザーは無料でGitHub Actionsを使用できます**
> APIの利用料金はAnthropic側が負担します

出典: https://zenn.dev/r_kaga/articles/731fe4636289dc

## 現在の状況

1. **OAuth認証は正しく設定済み**
   - CLAUDE_CODE_OAUTH_TOKEN ✓

2. **課金エラーが発生している理由**
   - 通常のGitHub Actionsが実行されている可能性
   - claude-code-action以外のアクションが課金対象になっている

## 解決策

### 1. claude-code-actionのみを使用する

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
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### 2. 他のワークフローを無効化

すでに実行済み：
- 課金が発生する可能性のあるワークフローを`.github/workflows-disabled/`に移動
- claude-code-actions.ymlのみを残す

### 3. テスト方法

1. **Issue作成でテスト**
   ```
   タイトル: テスト
   本文: @claude こんにちは
   ```

2. **手動ワークフロー実行**
   - Actions → Minimal Claude Test → Run workflow

## 注意事項

- **claude-code-action以外のステップは課金対象**
- **checkout、setup-python等も課金対象になる可能性**
- **純粋にclaude-code-actionのみを使用すること**

## 確認事項

もし引き続きエラーが発生する場合：

1. Anthropicアカウントの確認
   - Claude Max Planが有効か
   - 認証が正しいか

2. GitHubアカウントの確認
   - 他のActionsが実行されていないか
   - 課金設定に制限がないか

3. claude-code-actionの最新情報
   - https://github.com/anthropics/claude-code-action
   - ドキュメントの更新を確認