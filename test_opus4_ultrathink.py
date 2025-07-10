#!/usr/bin/env python3
"""
Realistic test for Opus4 with ultrathink mode
"""

import requests
import concurrent.futures
import time
from datetime import datetime
import json

# Configuration
BASE_URL = "http://localhost:8001"
BATCH_SIZE = 5  # Max parallel requests per batch
NUM_BATCHES = 10  # Total batches to run
BATCH_DELAY = 60  # Seconds between batches

# Test messages requiring deep thinking
TEST_MESSAGES = [
    "ultrathink: この文章の論理的矛盾を分析してください：「すべての規則には例外がある」という規則自体は例外を持つか？",
    "ultrathink: P=NP問題について、現在の研究状況と主要な取り組みを要約してください",
    "ultrathink: 量子コンピューティングが古典的暗号システムに与える影響を詳しく説明してください",
    "ultrathink: 意識のハードプロブレムについて、主要な哲学的立場を比較してください",
    "ultrathink: ゲーデルの不完全性定理の意味と数学への影響を説明してください"
]

def test_ultrathink_request(batch_id, req_id):
    """Test a single ultrathink request"""
    message = TEST_MESSAGES[req_id % len(TEST_MESSAGES)]
    start_time = time.time()
    
    print(f"[Batch {batch_id+1}, Request {req_id+1}] Starting ultrathink request...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                'message': message,
                'model': 'opus4'
            },
            timeout=1800  # 30 minute timeout for ultrathink
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('message', '')
            
            print(f"[Batch {batch_id+1}, Request {req_id+1}] ✓ Success in {duration:.1f}s")
            
            return {
                'batch': batch_id,
                'request': req_id,
                'success': True,
                'duration': duration,
                'response_length': len(response_text),
                'message': message[:50] + '...'
            }
        else:
            print(f"[Batch {batch_id+1}, Request {req_id+1}] ✗ HTTP {response.status_code}")
            return {
                'batch': batch_id,
                'request': req_id,
                'success': False,
                'duration': duration,
                'error': f"HTTP {response.status_code}",
                'message': message[:50] + '...'
            }
            
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"[Batch {batch_id+1}, Request {req_id+1}] ✗ Timeout after {duration:.1f}s")
        return {
            'batch': batch_id,
            'request': req_id,
            'success': False,
            'duration': duration,
            'error': "Timeout",
            'message': message[:50] + '...'
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"[Batch {batch_id+1}, Request {req_id+1}] ✗ Error: {str(e)[:50]}")
        return {
            'batch': batch_id,
            'request': req_id,
            'success': False,
            'duration': duration,
            'error': str(e)[:100],
            'message': message[:50] + '...'
        }

def run_realistic_test():
    """Run realistic ultrathink test"""
    print(f"Starting Opus4 ultrathink test")
    print(f"Configuration: {NUM_BATCHES} batches × {BATCH_SIZE} parallel requests")
    print(f"Expected total: {NUM_BATCHES * BATCH_SIZE} requests")
    print("=" * 80)
    
    all_results = []
    
    for batch_id in range(NUM_BATCHES):
        print(f"\n🚀 Starting Batch {batch_id+1}/{NUM_BATCHES} at {datetime.now().strftime('%H:%M:%S')}")
        
        # Run batch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = [
                executor.submit(test_ultrathink_request, batch_id, req_id)
                for req_id in range(BATCH_SIZE)
            ]
            
            # Collect results
            batch_results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                batch_results.append(result)
                all_results.append(result)
        
        # Batch summary
        batch_success = len([r for r in batch_results if r['success']])
        avg_duration = sum(r['duration'] for r in batch_results) / len(batch_results)
        
        print(f"\nBatch {batch_id+1} Summary:")
        print(f"  Success rate: {batch_success}/{BATCH_SIZE}")
        print(f"  Average duration: {avg_duration:.1f}s")
        
        # Check if we should continue
        if batch_success == 0:
            print("\n⚠️  All requests failed in this batch. Stopping test.")
            break
        
        # Wait before next batch
        if batch_id < NUM_BATCHES - 1:
            print(f"\n⏳ Waiting {BATCH_DELAY}s before next batch...")
            time.sleep(BATCH_DELAY)
    
    # Final report
    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    
    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]
    
    print(f"Total requests: {len(all_results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(all_results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(all_results)*100:.1f}%)")
    
    if successful:
        durations = [r['duration'] for r in successful]
        print(f"\nDuration statistics (successful):")
        print(f"  Min: {min(durations):.1f}s")
        print(f"  Max: {max(durations):.1f}s")
        print(f"  Average: {sum(durations)/len(durations):.1f}s")
        
        response_lengths = [r['response_length'] for r in successful]
        print(f"\nResponse length statistics:")
        print(f"  Min: {min(response_lengths):,} chars")
        print(f"  Max: {max(response_lengths):,} chars")
        print(f"  Average: {sum(response_lengths)//len(response_lengths):,} chars")
    
    if failed:
        print(f"\nError breakdown:")
        error_counts = {}
        for r in failed:
            error = r.get('error', 'Unknown')
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error}: {count}")
    
    # Save results
    with open('/home/ubuntu/webai/opus4_ultrathink_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to opus4_ultrathink_results.json")

if __name__ == "__main__":
    print("⚠️  WARNING: This test will use significant API tokens!")
    print("Each ultrathink request can use up to 32,000 tokens.")
    print(f"Estimated maximum token usage: {NUM_BATCHES * BATCH_SIZE * 32000:,} tokens")
    print("\nAutomatic execution mode - starting test...")
    run_realistic_test()