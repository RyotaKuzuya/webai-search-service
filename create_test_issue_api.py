#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

# GitHub API設定
GITHUB_TOKEN = "[REMOVED]"
OWNER = "RyotaKuzuya"
REPO = "webai-search-service"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

print("🧪 Claude Max Plan GitHub Actions テスト")
print("========================================")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. 新しいIssueを作成
print("📝 新しいテストIssueを作成中...")

issue_data = {
    "title": f"Max Plan Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "body": "このIssueは、Claude Max Plan (v1.0.44+) のGitHub Actions統合をテストするために作成されました。\n\n以下のコメントでClaudeをテストします。",
    "labels": ["test", "claude-test"]
}

create_response = requests.post(
    f"https://api.github.com/repos/{OWNER}/{REPO}/issues",
    headers=headers,
    json=issue_data
)

if create_response.status_code == 201:
    issue = create_response.json()
    issue_number = issue["number"]
    issue_url = issue["html_url"]
    
    print(f"✅ Issue #{issue_number} を作成しました")
    print(f"   URL: {issue_url}")
    print()
    
    # 少し待つ
    time.sleep(2)
    
    # 2. @claudeメンションでコメント
    print("💬 @claudeメンションでコメントを投稿中...")
    
    comment_data = {
        "body": """@claude

Max Plan (v1.0.44+) の動作テストです。

以下を確認してください：
1. このメッセージに正常に応答できますか？
2. GitHub Actionsは無料で動作していますか？
3. startup_failureエラーは解消されましたか？

簡潔に回答してください。"""
    }
    
    comment_response = requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{issue_number}/comments",
        headers=headers,
        json=comment_data
    )
    
    if comment_response.status_code == 201:
        comment = comment_response.json()
        print(f"✅ コメントを投稿しました")
        print(f"   URL: {comment['html_url']}")
        print()
        
        # 3. GitHub Actionsの状態を確認
        print("⏳ 10秒待機後、GitHub Actionsを確認...")
        time.sleep(10)
        
        actions_response = requests.get(
            f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page=5",
            headers=headers
        )
        
        if actions_response.status_code == 200:
            runs = actions_response.json()["workflow_runs"]
            
            print()
            print("📊 最新のワークフロー実行:")
            for run in runs[:3]:
                status_icon = "✅" if run['conclusion'] == "success" else "❌" if run['conclusion'] else "⏳"
                print(f"{status_icon} {run['name']}: {run['status']} ({run['conclusion'] or '実行中'})")
                print(f"   作成: {run['created_at']}")
                
                # 新しいワークフローかチェック
                if "Claude Max Plan" in run['name'] or run['created_at'] > comment['created_at']:
                    print(f"   🆕 新しいワークフロー！")
        
        print()
        print("="*50)
        print()
        print("📋 確認事項:")
        print(f"1. Issue: {issue_url}")
        print(f"2. Actions: https://github.com/{OWNER}/{REPO}/actions")
        print()
        print("⏰ Claudeの応答を待っています...")
        print("   通常1-2分以内に応答があります")
        
    else:
        print(f"❌ コメント投稿エラー: {comment_response.status_code}")
        print(comment_response.text)
        
else:
    print(f"❌ Issue作成エラー: {create_response.status_code}")
    print(create_response.text)