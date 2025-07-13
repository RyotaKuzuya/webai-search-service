# Claude Code Actions と GitHub Actions の違い

## 🎯 根本的な違い

### GitHub Actions
- **提供者**: GitHub (Microsoft)
- **役割**: CI/CDプラットフォーム、ワークフロー実行環境
- **料金**: GitHubが課金（Privateリポは有料）
- **内容**: 仮想マシン、実行時間、ストレージ

### Claude Code Actions
- **提供者**: Anthropic
- **役割**: GitHub Actions上で動くAIアシスタント機能
- **料金**: Claude API使用料（Max Planでカバー）
- **内容**: AIによるコード生成、レビュー、質問応答

## 📊 関係性の図解

```
┌─────────────────────────────────────┐
│        GitHub Actions               │
│  （実行環境・インフラ）              │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Claude Code Actions        │   │
│  │  (AIアシスタント機能)        │   │
│  └─────────────────────────────┘   │
│                                     │
│  料金: GitHub が請求              │
└─────────────────────────────────────┘
         ↓
    Claude API呼び出し
         ↓
┌─────────────────────────────────────┐
│      Anthropic Claude API          │
│  料金: Max Plan でカバー           │
└─────────────────────────────────────┘
```

## 💰 料金の内訳

### 1. GitHub Actions実行時
- **インフラコスト**: GitHub に支払い
  - Ubuntu runner: $0.008/分
  - Privateリポ: 無料枠2,000分/月
  
### 2. Claude API使用時
- **AI処理コスト**: Anthropic に支払い
  - 通常: 従量課金
  - Max Plan: 月額料金に含まれる

## 🔍 具体例

```yaml
name: Example Workflow
on: [push]

jobs:
  example:
    runs-on: ubuntu-latest  # ← GitHub Actions (有料部分)
    steps:
      - uses: anthropics/claude-code-action@v1  # ← Claude Code Actions
        with:
          claude_code_oauth_token: ${{ secrets.TOKEN }}  # ← Max Planでカバー
```

この例では：
- `runs-on: ubuntu-latest` → GitHub が課金
- `claude-code-action` の処理 → Max Plan でカバー

## ❓ よくある誤解

### ❌ 間違い
「Claude Max Plan があれば GitHub Actions も無料で使える」

### ✅ 正解
「Claude Max Plan は Claude API 使用料のみカバー。GitHub Actions の実行環境は別料金」

## 🎪 アナロジー（例え）

**GitHub Actions** = レンタカー（車両・ガソリン代）
**Claude Code Actions** = カーナビアプリ（道案内サービス）

Max Plan は「カーナビアプリ使い放題」であって、「レンタカー代無料」ではない。

## 💡 結論

1. **Claude Code Actions**: AIアシスタント機能（ソフトウェア）
2. **GitHub Actions**: 実行環境（インフラストラクチャ）
3. **Max Plan**: AI機能のみカバー、インフラは別

だから Private リポジトリで GitHub Actions を使うと課金される。