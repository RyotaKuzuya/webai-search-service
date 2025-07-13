#!/usr/bin/env python3
"""
Parallel testing script for WebAI service
Tests multiple concurrent requests to identify issues
"""

import requests
import concurrent.futures
import time
import json
from datetime import datetime
import statistics

# Configuration
BASE_URL = "http://localhost:8001"
NUM_TESTS = 30  # Number of parallel tests
TEST_MESSAGES = [
    "こんにちは",
    "今日の天気は？",
    "Pythonの基本的な文法を教えて",
    "エラーが発生しました。 (Unexpected token '",
    "シンプルなテストメッセージ",
    "1 + 1 = ?",
    "Hello world",
    "テスト",
    "AIについて教えて",
    "プログラミングの基礎"
]

def test_single_request(test_id, message):
    """Test a single request to the API"""
    start_time = time.time()
    result = {
        'test_id': test_id,
        'message': message,
        'start_time': datetime.now().isoformat(),
        'success': False,
        'response_time': None,
        'error': None,
        'response': None
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                'message': message,
                'model': 'haiku'  # Use haiku for faster responses
            },
            timeout=120  # 2 minute timeout
        )
        
        result['response_time'] = time.time() - start_time
        result['status_code'] = response.status_code
        
        if response.status_code == 200:
            data = response.json()
            result['success'] = True
            result['response'] = data.get('message', '')[:100]  # First 100 chars
        else:
            result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        result['response_time'] = time.time() - start_time
        result['error'] = "Request timeout"
    except requests.exceptions.ConnectionError:
        result['response_time'] = time.time() - start_time
        result['error'] = "Connection error"
    except Exception as e:
        result['response_time'] = time.time() - start_time
        result['error'] = str(e)
    
    return result

def run_parallel_tests():
    """Run tests in parallel"""
    print(f"Starting {NUM_TESTS} parallel tests at {datetime.now()}")
    print("=" * 80)
    
    # Create test cases
    test_cases = []
    for i in range(NUM_TESTS):
        message = TEST_MESSAGES[i % len(TEST_MESSAGES)]
        test_cases.append((i, message))
    
    # Run tests in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_TESTS) as executor:
        future_to_test = {
            executor.submit(test_single_request, test_id, msg): (test_id, msg) 
            for test_id, msg in test_cases
        }
        
        for future in concurrent.futures.as_completed(future_to_test):
            test_id, msg = future_to_test[future]
            try:
                result = future.result()
                results.append(result)
                
                # Print progress
                status = "✓" if result['success'] else "✗"
                print(f"{status} Test {result['test_id']:3d}: {result['response_time']:.2f}s - {result['error'] or 'Success'}")
                
            except Exception as e:
                print(f"✗ Test {test_id}: Exception - {str(e)}")
    
    # Analyze results
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    
    if successful:
        response_times = [r['response_time'] for r in successful]
        print(f"\nResponse time statistics (successful requests):")
        print(f"  Min: {min(response_times):.2f}s")
        print(f"  Max: {max(response_times):.2f}s")
        print(f"  Average: {statistics.mean(response_times):.2f}s")
        print(f"  Median: {statistics.median(response_times):.2f}s")
    
    if failed:
        print(f"\nError breakdown:")
        error_counts = {}
        for r in failed:
            error_type = r['error'].split(':')[0] if r['error'] else 'Unknown'
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_type}: {count}")
    
    # Save detailed results
    with open('/home/ubuntu/webai/test_results.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to test_results.json")
    
    # Check for blank responses
    blank_responses = [r for r in successful if not r['response'] or r['response'].strip() == '']
    if blank_responses:
        print(f"\nWARNING: {len(blank_responses)} blank responses detected!")

if __name__ == "__main__":
    run_parallel_tests()