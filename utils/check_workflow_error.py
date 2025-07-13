#!/usr/bin/env python3
import requests
import json

print("🔍 ワークフローエラーの詳細確認")
print("================================")
print()

# 最新のワークフロー実行を取得
url = "https://api.github.com/repos/RyotaKuzuya/webai-search-service/actions/runs?per_page=1"
response = requests.get(url)

if response.status_code == 200:
    run = response.json()["workflow_runs"][0]
    run_id = run["id"]
    
    print(f"ワークフロー: {run['name']}")
    print(f"状態: {run['conclusion']}")
    print(f"URL: {run['html_url']}")
    print()
    
    # ジョブの詳細を取得
    jobs_url = f"https://api.github.com/repos/RyotaKuzuya/webai-search-service/actions/runs/{run_id}/jobs"
    jobs_response = requests.get(jobs_url)
    
    if jobs_response.status_code == 200:
        jobs = jobs_response.json()["jobs"]
        for job in jobs:
            print(f"ジョブ: {job['name']}")
            print(f"結論: {job['conclusion']}")
            
            if job.get("steps"):
                print("ステップ:")
                for step in job["steps"]:
                    icon = "✅" if step.get("conclusion") == "success" else "❌"
                    print(f"  {icon} {step['name']}: {step.get('conclusion', 'pending')}")

print()
print("📝 考えられる原因:")
print("1. CLAUDE_CODE_OAUTH_TOKEN の形式が間違っている")
print("2. トークンの有効期限切れ")
print("3. アクションのバージョン問題")
print()
print("解決方法:")
print("1. 新しいOAuthトークンを生成: claude setup-token")
print("2. GitHub Secretsを更新")
print("3. ワークフローのログを確認: " + run['html_url'])