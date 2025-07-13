# 記事の「MAXプランで使う方法」追記部分の内容

## 📅 2025年7月13日追記の内容

記事では、MAX プランでClaude Code Actionsを使う方法を説明しています：

### 1. トークン生成手順
```bash
claude setup-token
```
実行後：
1. URLが表示される
2. ブラウザでURLにアクセス
3. 「承認する」をクリック
4. 認証コードをコピー
5. ターミナルに貼り付け
6. `sk`で始まるトークンが生成される

### 2. GitHub設定
1. リポジトリのSettings
2. Secrets and variables → Actions
3. New repository secret
4. 名前: `CLAUDE_CODE_OAUTH_TOKEN`
5. 値: 生成されたトークン

### 3. YAMLファイルの修正
```yaml
# 変更前
- anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# 変更後
+ claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## ⚠️ 重要な点

この記事も**GitHub Actionsを使用する前提**です！

つまり：
- Claude API料金 → MAX Planでカバー ✅
- GitHub Actions実行料金 → 別途必要 💰

## 🤔 混乱の原因

記事のタイトルや内容が「MAXプランで使える」と強調しているため、「すべて無料」と誤解しやすいですが：

1. **MAXプランでカバーされるもの**
   - Claude APIの使用料のみ

2. **MAXプランでカバーされないもの**
   - GitHub Actionsの実行環境料金

## 📊 実際のコスト

```
総コスト = GitHub Actions料金 + Claude API料金
         = 有料（Private repo） + 0円（MAX Plan）
         = 有料
```

## ✅ 結論

記事の追記部分も、GitHub Actions上でClaude Code Actionsを使う方法であり、GitHub Actionsの料金は避けられません。

完全無料にするには：
1. リポジトリをPublicにする
2. またはローカル実行のみ使用する