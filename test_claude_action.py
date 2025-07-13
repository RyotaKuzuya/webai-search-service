#!/usr/bin/env python3

import subprocess
import time
import requests
import json

print("🧪 Claude Max Plan Action テスト")
print("=================================")
print()

# テスト用のIssue内容
issue_title = "Claude Max Plan Test - All 3 Tokens"
issue_body = """Testing Claude Code Action with complete token setup:
- CLAUDE_ACCESS_TOKEN ✅
- CLAUDE_REFRESH_TOKEN ✅  
- CLAUDE_EXPIRES_AT ✅

Automated test at: {}
""".format(time.strftime("%Y-%m-%d %H:%M:%S"))

comment_body = """@claude
こんにちは！3つのトークンすべてを設定してテストしています。
このメッセージに応答してください。"""

print("📝 テスト内容:")
print(f"タイトル: {issue_title}")
print(f"本文: {issue_body[:50]}...")
print()

# GitHub CLIを使用してIssue作成
print("⏳ Issueを作成中...")
try:
    result = subprocess.run(
        ["gh", "issue", "create", 
         "--repo", "RyotaKuzuya/webai-search-service",
         "--title", issue_title,
         "--body", issue_body],
        capture_output=True,
        text=True,
        check=True
    )
    
    issue_url = result.stdout.strip()
    issue_num = issue_url.split("/")[-1]
    
    print(f"✅ Issue作成成功！")
    print(f"URL: {issue_url}")
    print()
    
    # 少し待機
    print("⏳ 2秒待機中...")
    time.sleep(2)
    
    # コメント追加
    print("💬 @claudeメンションを追加中...")
    subprocess.run(
        ["gh", "issue", "comment", issue_num,
         "--repo", "RyotaKuzuya/webai-search-service", 
         "--body", comment_body],
        check=True
    )
    
    print("✅ コメント追加完了！")
    print()
    
    print("📊 確認リンク:")
    print(f"1. Issue: {issue_url}")
    print(f"2. Actions: https://github.com/RyotaKuzuya/webai-search-service/actions")
    print()
    print("🎉 テスト開始しました！数秒後にActionsタブを確認してください。")
    
except subprocess.CalledProcessError as e:
    print(f"❌ エラーが発生しました: {e}")
    print()
    print("手動でテストしてください:")
    print("1. https://github.com/RyotaKuzuya/webai-search-service/issues/new")
    print("2. 上記の内容でIssue作成")
    print("3. コメントで @claude メンション")
except FileNotFoundError:
    print("❌ GitHub CLI (gh) がインストールされていません")
    print()
    print("手動でテストするか、以下のリンクから:")
    print("https://github.com/RyotaKuzuya/webai-search-service/issues/new")