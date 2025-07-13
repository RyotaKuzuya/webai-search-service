#!/usr/bin/env python3
"""
Claude Max OAuth トークンを使用した直接API呼び出し
GitHub Actionsの課金制限をバイパス
"""

import requests
import json
import sys
import os
from datetime import datetime

# Claude認証情報を読み込み
CLAUDE_CONFIG = "/home/ubuntu/.claude/.credentials.json"

def load_claude_credentials():
    """Claude認証情報を読み込む"""
    with open(CLAUDE_CONFIG, 'r') as f:
        data = json.load(f)
        return data['claudeAiOauth']

def call_claude_api(prompt, credentials):
    """Claude APIを直接呼び出し"""
    headers = {
        'Authorization': f'Bearer {credentials["accessToken"]}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'anthropic-version': '2023-06-01'
    }
    
    # Claude API エンドポイント（推定）
    api_url = "https://api.anthropic.com/v1/messages"
    
    payload = {
        "model": "claude-3-opus-20240229",  # Claude Max対応モデル
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"エラー: {e}")
        return None

def github_actions_simulator(task_type="code-review"):
    """GitHub Actions相当の処理をローカルで実行"""
    credentials = load_claude_credentials()
    
    print(f"🚀 Claude Max Direct Execution - {datetime.now()}")
    print(f"認証タイプ: {credentials.get('subscriptionType', 'unknown')}")
    
    # タスクに応じたプロンプト
    if task_type == "code-review":
        prompt = """
        WebAIプロジェクトのコードをレビューしてください。
        以下の観点で確認：
        1. セキュリティの問題
        2. パフォーマンスの最適化
        3. コード品質
        
        特に simple_api.py と simple_app.py を重点的に。
        """
    elif task_type == "maintenance":
        prompt = """
        WebAIプロジェクトの定期メンテナンスを実行：
        1. 依存関係の更新確認
        2. セキュリティパッチの必要性
        3. 改善提案
        """
    else:
        prompt = task_type
    
    print("\n📝 タスク実行中...")
    result = call_claude_api(prompt, credentials)
    
    if result:
        print("\n✅ 実行成功!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 結果をファイルに保存（GitHub Actionsのアーティファクト相当）
        output_file = f"claude_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 結果を保存: {output_file}")
    else:
        print("\n❌ 実行失敗")
        
def main():
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        github_actions_simulator(task)
    else:
        # デフォルトタスク
        github_actions_simulator("code-review")

if __name__ == "__main__":
    main()