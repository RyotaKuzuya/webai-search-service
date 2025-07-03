# GitHub Actions 支払い・制限問題の対策

## 問題
- サブスクリプションでもワークフローが実行できない
- 「The job was not started because recent account payments have failed or your spending limit needs to be increased」エラー

## 対策

### 1. 支出制限の確認と更新
```
Settings > Billing and plans > Spending limits
```
- デフォルトは$0に設定されている
- 必要に応じて制限を引き上げる（例：$15）

### 2. 新しい予算システムへの対応
GitHubは「Spending Limits」から「Budgets」システムに移行
```
Settings > Billing > Budgets
```
- GitHub Actions用の予算を設定
- Codespaces、LFS用の予算も個別に設定

### 3. 無料プランでの対策
パブリックリポジトリの場合：
- 標準のGitHub-hostedランナーは無料
- ストレージと帯域幅は課金対象になる可能性

### 4. ワークフロー最適化
```yaml
# .github/workflows/optimize.yml
name: Optimized Workflow

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10  # タイムアウト設定
    
    steps:
    - uses: actions/checkout@v3
    
    # キャッシュの活用
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.npm
          ~/.cache
        key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
    
    # 必要な時のみ実行
    - name: Check for changes
      uses: dorny/paths-filter@v2
      id: changes
      with:
        filters: |
          src:
            - 'src/**'
            - 'package.json'
    
    - name: Build
      if: steps.changes.outputs.src == 'true'
      run: npm run build
```

### 5. セルフホストランナーの使用
無料でワークフローを実行するため：
```bash
# セルフホストランナーのセットアップ
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN
./run.sh
```

### 6. ワークフロー使用量の監視
```yaml
# 使用量レポート用ワークフロー
name: Usage Report

on:
  schedule:
    - cron: '0 0 * * 0'  # 週次実行

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
    - name: Get usage
      run: |
        echo "Check usage at: https://github.com/settings/billing"
```

### 7. 代替CI/CDサービスの検討
- GitLab CI/CD（無料枠あり）
- CircleCI（無料枠あり）
- Travis CI
- Jenkins（セルフホスト）

### 8. GitHub Supportへの連絡
上記で解決しない場合：
1. https://support.github.com へアクセス
2. Billing issueとして報告
3. エラーメッセージとスクリーンショットを添付

## 即時対応策

### WebAIプロジェクト用の設定
```yaml
# .github/workflows/webai-deploy.yml
name: WebAI Deploy

on:
  push:
    branches: [ master ]
    paths:
      - '**.py'
      - 'requirements.txt'
      - 'templates/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.repository_owner == 'RyotaKuzuya'  # オーナー確認
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 1  # 浅いクローン
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'pip'
    
    - name: Deploy notification
      run: echo "Deploy completed"
```

## 予防策
1. 定期的な支払い情報の確認
2. 使用量アラートの設定（75%, 90%, 100%）
3. 不要なワークフローの削除
4. プライベートリポジトリの使用を最小限に