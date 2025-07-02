#!/usr/bin/env python3
"""
Simplified Claude bridge that provides basic responses
"""

import os
import json
import logging
import time

logger = logging.getLogger(__name__)

class SimpleClaudeBridge:
    """Simple bridge for basic chat functionality"""
    
    def __init__(self):
        self.is_available = True
        logger.info("Simple Claude Bridge initialized")
    
    def check_bridge(self):
        """Always available"""
        return self.is_available
    
    def send_message(self, message, model="claude-opus-4-20250514", web_search=True):
        """Send message and return a simple response"""
        try:
            logger.info(f"Processing message: {message[:50]}...")
            
            # Simple response logic
            responses = []
            
            if "hello" in message.lower() or "こんにちは" in message.lower():
                responses = [
                    "こんにちは！WebAIチャットサービスへようこそ。",
                    "どのようなことでお手伝いできますか？"
                ]
            elif "test" in message.lower():
                responses = [
                    "テストメッセージを受信しました。",
                    "WebAIは正常に動作しています。",
                    "Claude統合は現在セットアップ中です。"
                ]
            elif "検索" in message or "search" in message.lower():
                responses = [
                    "Web検索機能は現在開発中です。",
                    "まもなく最新の情報を検索できるようになります。"
                ]
            else:
                responses = [
                    f"あなたのメッセージ「{message[:30]}...」を受信しました。",
                    "現在、基本的な応答モードで動作しています。",
                    "完全なClaude AI統合は準備中です。"
                ]
            
            # Stream responses
            for response in responses:
                yield json.dumps({
                    "content": response
                }) + "\n"
                time.sleep(0.1)  # Simulate typing
            
            yield json.dumps({
                "status": "complete"
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            yield json.dumps({
                "error": f"エラーが発生しました: {str(e)}"
            }) + "\n"