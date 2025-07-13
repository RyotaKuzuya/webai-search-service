#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

print("🧪 Claude Max Plan GitHub Actions 最終テスト")
print("==========================================")
print()
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# リポジトリ情報
OWNER = "RyotaKuzuya"
REPO = "webai-search-service"

# 1. リポジトリ状態を確認
print("1️⃣ リポジトリ状態の確認...")
repo_url = f"https://api.github.com/repos/{OWNER}/{REPO}"
repo_response = requests.get(repo_url)

if repo_response.status_code == 200:
    repo_data = repo_response.json()
    print(f"   ✅ リポジトリ: {repo_data['full_name']}")
    print(f"   ✅ 状態: {'Public' if not repo_data['private'] else 'Private'}")
    print(f"   ✅ URL: {repo_data['html_url']}")
else:
    print("   ❌ リポジトリ情報の取得に失敗")

print()

# 2. 最新のワークフロー実行を確認
print("2️⃣ GitHub Actions の状態確認...")
actions_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page=5"
actions_response = requests.get(actions_url)

if actions_response.status_code == 200:
    runs = actions_response.json()["workflow_runs"]
    if runs:
        print("   最新のワークフロー実行:")
        for i, run in enumerate(runs[:3]):
            status_icon = "✅" if run['conclusion'] == "success" else "❌" if run['conclusion'] else "⏳"
            print(f"   {status_icon} {run['name'] or 'Unknown'}: {run['status']} ({run['conclusion'] or '実行中'})")
            print(f"      作成: {run['created_at']}")
    else:
        print("   ⚠️ ワークフロー実行履歴なし")
else:
    print("   ❌ Actions情報の取得に失敗")

print()

# 3. Issue #4 の最新コメントを確認
print("3️⃣ Issue #4 のコメント確認...")
comments_url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/4/comments?per_page=5"
comments_response = requests.get(comments_url)

if comments_response.status_code == 200:
    comments = comments_response.json()
    if comments:
        print("   最新のコメント:")
        for comment in comments[:3]:
            user = comment['user']['login']
            created = comment['created_at']
            body_preview = comment['body'][:50].replace('\n', ' ')
            print(f"   • {user}: {body_preview}... ({created})")
    else:
        print("   ⚠️ コメントなし")

print()
print("="*50)
print()
print("📝 テスト手順:")
print()
print("1. 以下のURLでIssue #4 にアクセス:")
print(f"   https://github.com/{OWNER}/{REPO}/issues/4")
print()
print("2. 以下のコメントを投稿:")
print("   ---")
print("   @claude")
print("   ")
print("   Max Plan サポートのテストです！")
print("   Claude Code v1.0.44+ で正常に動作することを確認してください。")
print("   ---")
print()
print("3. 結果を確認:")
print(f"   • Actions: https://github.com/{OWNER}/{REPO}/actions")
print(f"   • Issue: https://github.com/{OWNER}/{REPO}/issues/4")
print()
print("✅ 期待される結果:")
print("   • startup_failure ではなく正常に実行")
print("   • Claude からの返信")
print("   • 課金エラーなし")