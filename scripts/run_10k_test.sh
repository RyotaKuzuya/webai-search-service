#!/bin/bash
# Run the 10,000 test in background with proper logging

echo "Starting Opus4 10,000 ultrathink test at $(date)"
echo "This will run in the background. Check opus4_10k_test.log for progress."
echo "To stop: kill \$(pgrep -f test_opus4_scale.py)"

cd /home/ubuntu/webai

# Run with unbuffered output
python3 -u test_opus4_scale.py > opus4_10k_test.log 2>&1 &

echo "Test started with PID: $!"
echo "Monitor with: tail -f opus4_10k_test.log"