#!/bin/bash

echo "📝 テスト用の新しいIssueを作成する手順"
echo "======================================"
echo ""
echo "GitHubで手動で実行してください："
echo ""
echo "1. 新しいIssueを作成："
echo "   https://github.com/RyotaKuzuya/webai-search-service/issues/new"
echo ""
echo "2. タイトル:"
echo "   Max Plan v1.0.44+ テスト"
echo ""
echo "3. 本文:"
echo "   このIssueは、最新のMax Planサポート機能をテストするためのものです。"
echo ""
echo "4. Issueを作成後、以下をコメント："
echo ""
echo "---コピー用---"
cat << 'EOF'
@claude

Claude Max Plan (v1.0.44+) のサポートをテストしています。

以下を確認してください：
1. このメッセージに正常に応答できますか？
2. startup_failureエラーは解消されましたか？
3. 無料で動作していますか？

よろしくお願いします。
EOF
echo "---ここまで---"
echo ""
echo "注意: 新しいワークフローはまだプッシュされていないため、"
echo "      古いワークフローで実行される可能性があります。"