#!/bin/bash

# Load Testing Script for IKODIO BugBounty Platform

set -e

echo "======================================"
echo "IKODIO Load Testing Suite"
echo "======================================"

# Configuration
LOCUST_FILE="backend/tests/load/test_scenarios.py"
HOST="${1:-http://localhost:8000}"
SCENARIO="${2:-load_test}"

# Check if Locust is installed
if ! command -v locust &> /dev/null; then
    echo "Locust not found. Installing..."
    pip install locust locust-plugins
fi

# Scenario configurations
case "$SCENARIO" in
    smoke)
        USERS=10
        SPAWN_RATE=2
        RUN_TIME="2m"
        echo "Running smoke test..."
        ;;
    load)
        USERS=500
        SPAWN_RATE=25
        RUN_TIME="10m"
        echo "Running load test..."
        ;;
    stress)
        USERS=1500
        SPAWN_RATE=100
        RUN_TIME="15m"
        echo "Running stress test..."
        ;;
    spike)
        USERS=2000
        SPAWN_RATE=200
        RUN_TIME="5m"
        echo "Running spike test..."
        ;;
    endurance)
        USERS=300
        SPAWN_RATE=10
        RUN_TIME="60m"
        echo "Running endurance test..."
        ;;
    breakpoint)
        USERS=5000
        SPAWN_RATE=500
        RUN_TIME="20m"
        echo "Running breakpoint test..."
        ;;
    *)
        echo "Unknown scenario: $SCENARIO"
        echo "Available scenarios: smoke, load, stress, spike, endurance, breakpoint"
        exit 1
        ;;
esac

# Create results directory
mkdir -p monitoring/load-tests/results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="monitoring/load-tests/results/${SCENARIO}_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo ""
echo "Test Configuration:"
echo "  Host: $HOST"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE"
echo "  Duration: $RUN_TIME"
echo "  Results: $RESULTS_DIR"
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s -o /dev/null -w "%{http_code}" "$HOST/health" | grep -q "200"; then
    echo "Warning: Backend is not responding at $HOST"
    echo "Please start the backend server first"
    exit 1
fi

echo "Backend is running. Starting load test..."
echo ""

# Run Locust in headless mode
locust \
    -f "$LOCUST_FILE" \
    --host="$HOST" \
    --users="$USERS" \
    --spawn-rate="$SPAWN_RATE" \
    --run-time="$RUN_TIME" \
    --headless \
    --html="$RESULTS_DIR/report.html" \
    --csv="$RESULTS_DIR/results" \
    --logfile="$RESULTS_DIR/locust.log" \
    --print-stats

echo ""
echo "======================================"
echo "Load test completed!"
echo "Results saved to: $RESULTS_DIR"
echo ""
echo "View HTML report:"
echo "  open $RESULTS_DIR/report.html"
echo ""
echo "View raw data:"
echo "  cat $RESULTS_DIR/results_stats.csv"
echo "======================================"

# Generate summary
echo ""
echo "Generating test summary..."
python3 -c "
import csv
import json
from datetime import datetime

stats_file = '$RESULTS_DIR/results_stats.csv'
summary = {
    'scenario': '$SCENARIO',
    'timestamp': datetime.now().isoformat(),
    'configuration': {
        'users': $USERS,
        'spawn_rate': $SPAWN_RATE,
        'duration': '$RUN_TIME',
        'host': '$HOST'
    },
    'results': {}
}

try:
    with open(stats_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        if rows:
            aggregated = rows[-1]  # Last row is aggregated stats
            summary['results'] = {
                'total_requests': aggregated.get('Request Count', '0'),
                'failure_count': aggregated.get('Failure Count', '0'),
                'median_response_time': aggregated.get('Median Response Time', '0'),
                'average_response_time': aggregated.get('Average Response Time', '0'),
                'min_response_time': aggregated.get('Min Response Time', '0'),
                'max_response_time': aggregated.get('Max Response Time', '0'),
                'requests_per_second': aggregated.get('Requests/s', '0'),
                'failures_per_second': aggregated.get('Failures/s', '0')
            }
    
    with open('$RESULTS_DIR/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print('Summary saved to: $RESULTS_DIR/summary.json')
except Exception as e:
    print(f'Error generating summary: {e}')
"

echo ""
echo "Done!"
