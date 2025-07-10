#!/usr/bin/env python3
"""
Monitor the 10,000 test progress
"""

import time
import json
import os

def monitor_test():
    """Monitor test progress"""
    print("🔍 Monitoring Opus4 10,000 test progress...")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 80)
    
    last_completed = 0
    
    while True:
        try:
            # Check if summary file exists
            if os.path.exists('/home/ubuntu/webai/opus4_scale_summary.json'):
                with open('/home/ubuntu/webai/opus4_scale_summary.json', 'r') as f:
                    summary = json.load(f)
                    print(f"\n✅ Test completed!")
                    print(f"Total: {summary['total_requests']:,}")
                    print(f"Success: {summary['successful']:,}")
                    print(f"Failed: {summary['failed']:,}")
                    print(f"Duration: {summary['duration_hours']:.2f} hours")
                    break
            
            # Check running processes
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'test_opus4_scale.py'], capture_output=True)
            if result.returncode != 0:
                print("\n❌ Test process not running!")
                break
            
            # Check claude processes
            result = subprocess.run(['pgrep', '-c', 'claude'], capture_output=True)
            claude_count = int(result.stdout.decode().strip()) if result.returncode == 0 else 0
            
            print(f"\r⏳ Active claude processes: {claude_count}", end="", flush=True)
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_test()