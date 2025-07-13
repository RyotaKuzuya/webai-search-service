#!/usr/bin/env python3
import requests
import json

print("🔍 Claude Code Action エラーの詳細調査")
print("=====================================")
print()

# 最新のワークフロー実行の詳細を取得
url = "https://api.github.com/repos/RyotaKuzuya/webai-search-service/actions/runs"
response = requests.get(url)

if response.status_code == 200:
    runs = response.json()["workflow_runs"]
    
    # startup_failureのワークフローを探す
    for run in runs[:5]:
        if run.get("conclusion") == "startup_failure":
            run_id = run["id"]
            print(f"❌ エラーのあるワークフロー:")
            print(f"   ID: {run_id}")
            print(f"   作成時刻: {run['created_at']}")
            print(f"   ワークフロー: {run.get('path', 'unknown')}")
            print()
            
            # ジョブの詳細を取得
            jobs_url = f"https://api.github.com/repos/RyotaKuzuya/webai-search-service/actions/runs/{run_id}/jobs"
            jobs_response = requests.get(jobs_url)
            
            if jobs_response.status_code == 200:
                jobs = jobs_response.json()["jobs"]
                for job in jobs:
                    print(f"   ジョブ: {job['name']}")
                    print(f"   結論: {job.get('conclusion')}")
                    
                    # ステップの詳細
                    if job.get("steps"):
                        for step in job["steps"]:
                            if step.get("conclusion") != "success":
                                print(f"   ❌ 失敗ステップ: {step['name']}")
                                print(f"      状態: {step.get('conclusion')}")
            
            print()
            print(f"   詳細URL: {run['html_url']}")
            print()
            break

print("📋 考えられる原因:")
print()
print("1. アクション名の問題")
print("   - 'anthropics/claude-code-action@v1' が正しいか")
print("   - バージョンタグ '@v1' が存在するか")
print()
print("2. 権限の問題")
print("   - GitHub App の権限設定")
print("   - リポジトリへのアクセス権限")
print()
print("3. Secrets の形式")
print("   - CLAUDE_CODE_OAUTH_TOKEN の形式が正しいか")
print("   - トークンが有効期限内か")