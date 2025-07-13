#!/usr/bin/env python3
"""
Stress test for WebAI service with higher load
"""

import requests
import concurrent.futures
import time
from datetime import datetime
import random

# Configuration
BASE_URL = "http://localhost:8001"
NUM_WAVES = 3  # Number of test waves
REQUESTS_PER_WAVE = 20  # Requests per wave
WAVE_DELAY = 5  # Seconds between waves

# Test different models and message types
TEST_CONFIGS = [
    {"model": "haiku", "message": "短いテスト"},
    {"model": "sonnet", "message": "中程度の複雑さのテスト。Pythonの関数について説明してください。"},
    {"model": "opus4", "message": "より複雑なテスト。機械学習の基本概念を初心者向けに説明してください。"},
    {"model": "haiku", "message": "エラーが発生しました。 (Unexpected token '"},
    {"model": "haiku", "message": "ultrathink: 深い思考が必要な質問"},
]

def test_request(wave_id, req_id):
    """Test a single request"""
    config = random.choice(TEST_CONFIGS)
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                'message': config['message'],
                'model': config['model']
            },
            timeout=30  # 30 second timeout for stress test
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            is_blank = not message or message.strip() == ''
            
            return {
                'wave': wave_id,
                'request': req_id,
                'success': True,
                'duration': duration,
                'model': config['model'],
                'blank': is_blank,
                'response_len': len(message)
            }
        else:
            return {
                'wave': wave_id,
                'request': req_id,
                'success': False,
                'duration': duration,
                'model': config['model'],
                'error': f"HTTP {response.status_code}",
                'details': response.text[:100]
            }
            
    except requests.exceptions.Timeout:
        return {
            'wave': wave_id,
            'request': req_id,
            'success': False,
            'duration': time.time() - start_time,
            'model': config['model'],
            'error': "Timeout"
        }
    except Exception as e:
        return {
            'wave': wave_id,
            'request': req_id,
            'success': False,
            'duration': time.time() - start_time,
            'model': config['model'],
            'error': str(e)[:100]
        }

def run_stress_test():
    """Run stress test with multiple waves"""
    print(f"Starting stress test: {NUM_WAVES} waves × {REQUESTS_PER_WAVE} requests")
    print("=" * 80)
    
    all_results = []
    
    for wave in range(NUM_WAVES):
        print(f"\n🌊 Wave {wave + 1}/{NUM_WAVES} starting...")
        wave_results = []
        
        # Launch all requests in this wave simultaneously
        with concurrent.futures.ThreadPoolExecutor(max_workers=REQUESTS_PER_WAVE) as executor:
            futures = [
                executor.submit(test_request, wave, req_id)
                for req_id in range(REQUESTS_PER_WAVE)
            ]
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                wave_results.append(result)
                
                # Print immediate feedback
                if result['success']:
                    status = "🟩" if not result.get('blank') else "🟨"
                    print(f"{status} Success: {result['duration']:.1f}s [{result['model']}]")
                else:
                    print(f"🟥 Failed: {result['error']} [{result['model']}]")
        
        all_results.extend(wave_results)
        
        # Summary for this wave
        wave_success = [r for r in wave_results if r['success']]
        wave_blank = [r for r in wave_success if r.get('blank')]
        print(f"\nWave {wave + 1} complete: {len(wave_success)}/{REQUESTS_PER_WAVE} successful, {len(wave_blank)} blank")
        
        # Wait before next wave (except after last wave)
        if wave < NUM_WAVES - 1:
            print(f"Waiting {WAVE_DELAY}s before next wave...")
            time.sleep(WAVE_DELAY)
    
    # Final analysis
    print("\n" + "=" * 80)
    print("STRESS TEST COMPLETE")
    print("=" * 80)
    
    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]
    blank = [r for r in successful if r.get('blank')]
    
    print(f"Total requests: {len(all_results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(all_results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(all_results)*100:.1f}%)")
    print(f"Blank responses: {len(blank)} ({len(blank)/len(successful)*100 if successful else 0:.1f}% of successful)")
    
    # Model breakdown
    print("\nResults by model:")
    model_stats = {}
    for r in all_results:
        model = r['model']
        if model not in model_stats:
            model_stats[model] = {'total': 0, 'success': 0, 'blank': 0, 'failed': 0}
        
        model_stats[model]['total'] += 1
        if r['success']:
            model_stats[model]['success'] += 1
            if r.get('blank'):
                model_stats[model]['blank'] += 1
        else:
            model_stats[model]['failed'] += 1
    
    for model, stats in model_stats.items():
        print(f"  {model}: {stats['success']}/{stats['total']} success, {stats['blank']} blank, {stats['failed']} failed")
    
    # Error analysis
    if failed:
        print("\nError types:")
        error_counts = {}
        for r in failed:
            error = r.get('error', 'Unknown')
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error}: {count}")

if __name__ == "__main__":
    run_stress_test()