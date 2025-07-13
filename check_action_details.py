#!/usr/bin/env python3
import requests
import json

# 最新のワークフロー実行を確認
print("🔍 GitHub Actions の詳細を確認中...")
print("=====================================")
print()

# 最新の実行を取得
url = "https://api.github.com/repos/RyotaKuzuya/webai-search-service/actions/runs"
response = requests.get(url)

if response.status_code == 200:
    runs = response.json()["workflow_runs"]
    if runs:
        latest_run = runs[0]
        run_id = latest_run["id"]
        
        print(f"📊 最新のワークフロー実行:")
        print(f"   ID: {run_id}")
        print(f"   名前: {latest_run['name'] or 'Claude Code Actions'}")
        print(f"   状態: {latest_run['status']}")
        print(f"   結論: {latest_run.get('conclusion', '実行中')}")
        print(f"   作成時刻: {latest_run['created_at']}")
        print()
        
        # ジョブの詳細を取得
        jobs_url = f"https://api.github.com/repos/RyotaKuzuya/webai-search-service/actions/runs/{run_id}/jobs"
        jobs_response = requests.get(jobs_url)
        
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()["jobs"]
            for job in jobs:
                print(f"📋 ジョブ詳細:")
                print(f"   名前: {job['name']}")
                print(f"   状態: {job['status']}")
                print(f"   結論: {job.get('conclusion', '実行中')}")
                print()
                
                # ステップの詳細
                if job.get("steps"):
                    print("   ステップ:")
                    for step in job["steps"]:
                        status_icon = "✅" if step.get("conclusion") == "success" else "❌"
                        print(f"   {status_icon} {step['name']}: {step.get('conclusion', 'pending')}")
        
        print()
        print("🔗 詳細を確認:")
        print(f"   {latest_run['html_url']}")
else:
    print("❌ データの取得に失敗しました")

print()
print("📝 CLAUDE_CODE_OAUTH_TOKEN の確認方法:")
print("1. https://github.com/RyotaKuzuya/webai-search-service/settings/secrets/actions")
print("2. 'CLAUDE_CODE_OAUTH_TOKEN' が存在するか確認")
print("3. 'Updated' の日付を確認（古い場合は更新が必要）")