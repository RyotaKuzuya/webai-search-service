#!/usr/bin/env python3
"""
Test script to investigate ultrathink mode behavior
"""
import subprocess
import os
import json

CLAUDE_CLI = "/home/ubuntu/.npm-global/bin/claude"

def test_ultrathink():
    """Test ultrathink mode with different approaches"""
    
    test_cases = [
        {
            "name": "Normal message",
            "message": "What is 2+2?",
            "model": "claude-3-5-haiku-20241022"
        },
        {
            "name": "Ultrathink prefix",
            "message": "ultrathink: What is the meaning of life?",
            "model": "claude-3-5-haiku-20241022"
        },
        {
            "name": "Ultrathink in message",
            "message": "Please use ultrathink mode to solve this complex problem: What is consciousness?",
            "model": "claude-3-5-haiku-20241022"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test['name']}")
        print(f"Model: {test['model']}")
        print(f"Message: {test['message'][:50]}...")
        print(f"{'='*60}")
        
        # Try with --print flag
        cmd = [CLAUDE_CLI, "--print", "--model", test['model']]
        
        try:
            result = subprocess.run(
                cmd,
                input=test['message'],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout for testing
            )
            
            print(f"Return code: {result.returncode}")
            print(f"Stdout length: {len(result.stdout)}")
            print(f"Stderr length: {len(result.stderr)}")
            
            if result.stdout:
                print(f"Stdout preview: {result.stdout[:200]}...")
            else:
                print("Stdout: (empty)")
                
            if result.stderr:
                print(f"Stderr: {result.stderr[:200]}...")
            else:
                print("Stderr: (empty)")
                
        except subprocess.TimeoutExpired:
            print("TIMEOUT after 30 seconds")
        except Exception as e:
            print(f"Error: {e}")
    
    # Also test with different output format
    print(f"\n{'='*60}")
    print("Testing with --output-format json")
    print(f"{'='*60}")
    
    cmd = [CLAUDE_CLI, "--print", "--output-format", "json", "--model", "claude-3-5-haiku-20241022"]
    try:
        result = subprocess.run(
            cmd,
            input="ultrathink: test",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500] if result.stdout else '(empty)'}")
        print(f"Stderr: {result.stderr[:500] if result.stderr else '(empty)'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ultrathink()