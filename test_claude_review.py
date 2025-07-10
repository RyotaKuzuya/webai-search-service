#!/usr/bin/env python3
"""
Claude Actions テスト用ファイル
このファイルには意図的にいくつかの問題を含めています
"""

import os
import subprocess

# セキュリティの問題: SQLインジェクションの脆弱性
def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    # 実際のDBクエリはしないが、危険なパターン
    return query

# パフォーマンスの問題: 非効率なループ
def inefficient_search(items, target):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == target:
                result.append(items[i])
    return result

# セキュリティの問題: コマンドインジェクション
def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.stdout

# 未使用の変数
unused_variable = "This is never used"

# エラーハンドリングなし
def risky_function():
    data = open("nonexistent.txt", "r").read()
    return data

print("テストファイルです")