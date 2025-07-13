#!/usr/bin/env python3
import requests
import json
import time

# GitHub API設定
GITHUB_TOKEN = "[REMOVED]"
OWNER = "RyotaKuzuya"
REPO = "webai-search-service"
ISSUE_NUMBER = 4

# APIヘッダー
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

print("🧪 Claude Code Actions テスト実行中...")
print("=====================================")
print()

# コメントを投稿
comment_body = """@claude

リポジトリがPublicになったので、GitHub Actionsが無料で使えるはずです。

以下を確認してください：
1. このメッセージに応答できますか？
2. GitHub Actionsは正常に動作していますか？
3. エラーなく実行できていますか？

簡潔に答えてください。"""

print(f"📝 Issue #{ISSUE_NUMBER} にコメントを投稿...")
comment_url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{ISSUE_NUMBER}/comments"

try:
    response = requests.post(comment_url, headers=headers, json={"body": comment_body})
    if response.status_code == 201:
        comment_data = response.json()
        print(f"✅ コメントを投稿しました")
        print(f"   URL: {comment_data['html_url']}")
    else:
        print(f"❌ エラー: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ エラー: {e}")

print()
print("⏳ GitHub Actionsの起動を待機中（10秒）...")
time.sleep(10)

# GitHub Actionsの状態を確認
print()
print("🔍 GitHub Actionsの状態を確認...")
actions_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"

try:
    response = requests.get(actions_url, headers=headers)
    if response.status_code == 200:
        runs = response.json()["workflow_runs"]
        if runs:
            latest_run = runs[0]
            print(f"📊 最新のワークフロー実行:")
            print(f"   状態: {latest_run['status']}")
            print(f"   結論: {latest_run.get('conclusion', '実行中')}")
            print(f"   ワークフロー: {latest_run['name']}")
            print(f"   作成時刻: {latest_run['created_at']}")
            print(f"   URL: {latest_run['html_url']}")
        else:
            print("❌ ワークフロー実行が見つかりません")
    else:
        print(f"❌ エラー: {response.status_code}")
except Exception as e:
    print(f"❌ エラー: {e}")

print()
print("📋 確認URL:")
print(f"   Issue: https://github.com/{OWNER}/{REPO}/issues/{ISSUE_NUMBER}")
print(f"   Actions: https://github.com/{OWNER}/{REPO}/actions")
print()
print("✅ テスト実行完了！")