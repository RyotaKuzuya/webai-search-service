#!/usr/bin/env python3
"""
Scalable test for Opus4 with ultrathink mode
Targets 10,000 requests with controlled parallelism
"""

import requests
import concurrent.futures
import time
from datetime import datetime
import json
import os
import signal
import sys

# Configuration
BASE_URL = "http://localhost:8001"
TARGET_REQUESTS = 10000
MAX_PARALLEL = 20  # Maximum parallel requests
BATCH_SIZE = 100  # Requests per batch
BATCH_DELAY = 30  # Seconds between batches

# Progress tracking
completed_requests = 0
start_time = None

# Test messages
ULTRATHINK_PROMPTS = [
    "ultrathink: 数学的帰納法の本質について説明してください",
    "ultrathink: チューリング機械の停止問題について詳しく説明してください",
    "ultrathink: ベイズ推定の原理と応用を説明してください",
    "ultrathink: 複雑系における創発現象について説明してください",
    "ultrathink: 言語の起源に関する主要な理論を比較してください"
]

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n⚠️  Test interrupted by user")
    print(f"Completed {completed_requests} requests before interruption")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def make_request(request_id):
    """Make a single request"""
    global completed_requests
    
    message = ULTRATHINK_PROMPTS[request_id % len(ULTRATHINK_PROMPTS)]
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                'message': message,
                'model': 'opus4'
            },
            timeout=1800  # 30 minutes
        )
        
        completed_requests += 1
        
        if response.status_code == 200:
            return {
                'id': request_id,
                'success': True,
                'status_code': response.status_code
            }
        else:
            return {
                'id': request_id,
                'success': False,
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        completed_requests += 1
        return {
            'id': request_id,
            'success': False,
            'error': "Timeout"
        }
    except Exception as e:
        completed_requests += 1
        return {
            'id': request_id,
            'success': False,
            'error': str(e)[:100]
        }

def run_batch(batch_num, batch_size):
    """Run a batch of requests"""
    print(f"\n📦 Batch {batch_num}: Starting {batch_size} requests...")
    
    batch_start = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
        # Submit all requests
        futures = []
        for i in range(batch_size):
            request_id = (batch_num - 1) * BATCH_SIZE + i
            if request_id >= TARGET_REQUESTS:
                break
            futures.append(executor.submit(make_request, request_id))
        
        # Process completions
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            
            # Progress update every 10 completions
            if completed % 10 == 0:
                elapsed = time.time() - start_time
                rate = completed_requests / elapsed
                eta = (TARGET_REQUESTS - completed_requests) / rate if rate > 0 else 0
                
                print(f"  Progress: {completed}/{len(futures)} in batch, "
                      f"{completed_requests}/{TARGET_REQUESTS} total, "
                      f"Rate: {rate:.1f} req/s, "
                      f"ETA: {eta/3600:.1f}h")
    
    batch_duration = time.time() - batch_start
    success_count = len([r for r in results if r['success']])
    
    print(f"  Batch {batch_num} complete: {success_count}/{len(results)} successful in {batch_duration:.1f}s")
    
    return results

def run_scale_test():
    """Run the scale test"""
    global start_time
    
    print("🚀 Starting Opus4 ultrathink scale test")
    print(f"Target: {TARGET_REQUESTS:,} requests")
    print(f"Max parallel: {MAX_PARALLEL}")
    print(f"Batch size: {BATCH_SIZE}")
    print("=" * 80)
    
    start_time = time.time()
    all_results = []
    
    # Calculate number of batches needed
    num_batches = (TARGET_REQUESTS + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_num in range(1, num_batches + 1):
        # Calculate batch size (last batch might be smaller)
        current_batch_size = min(BATCH_SIZE, TARGET_REQUESTS - (batch_num - 1) * BATCH_SIZE)
        
        if current_batch_size <= 0:
            break
        
        # Run batch
        batch_results = run_batch(batch_num, current_batch_size)
        all_results.extend(batch_results)
        
        # Check if we should stop
        if completed_requests >= TARGET_REQUESTS:
            print(f"\n✅ Reached target of {TARGET_REQUESTS} requests!")
            break
        
        # Wait between batches
        if batch_num < num_batches:
            print(f"\n⏳ Waiting {BATCH_DELAY}s before next batch...")
            time.sleep(BATCH_DELAY)
    
    # Final report
    total_duration = time.time() - start_time
    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]
    
    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print(f"Total requests: {len(all_results):,}")
    print(f"Successful: {len(successful):,} ({len(successful)/len(all_results)*100:.1f}%)")
    print(f"Failed: {len(failed):,} ({len(failed)/len(all_results)*100:.1f}%)")
    print(f"Total duration: {total_duration/3600:.2f} hours")
    print(f"Average rate: {len(all_results)/total_duration:.2f} requests/second")
    
    if failed:
        print(f"\nError breakdown:")
        error_counts = {}
        for r in failed:
            error = r.get('error', 'Unknown')
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error}: {count:,}")
    
    # Save summary
    summary = {
        'total_requests': len(all_results),
        'successful': len(successful),
        'failed': len(failed),
        'duration_hours': total_duration/3600,
        'requests_per_second': len(all_results)/total_duration,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('/home/ubuntu/webai/opus4_scale_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to opus4_scale_summary.json")

if __name__ == "__main__":
    print("⚠️  EXTREME WARNING: This test will attempt 10,000 ultrathink requests!")
    print("Estimated token usage: up to 320,000,000 tokens (10,000 × 32,000)")
    print("This exceeds the daily MAX20 limit of 140,000 tokens by 2,285x!")
    print("\nThis test will likely:")
    print("- Hit rate limits very quickly")
    print("- Take many hours or days to complete")
    print("- Cost significant API usage")
    print("\nAutomatic execution mode - starting scale test...")
    print("Press Ctrl+C to stop at any time")
    run_scale_test()