"""
Locust configuration for load testing
"""

# Test configurations
LOCUST_CONFIG = {
    "host": "http://localhost:8000",
    "users": 1000,
    "spawn_rate": 50,
    "run_time": "10m",
}

# Scenario configurations
SCENARIOS = {
    "smoke_test": {
        "users": 10,
        "spawn_rate": 2,
        "run_time": "2m",
        "description": "Basic functionality test"
    },
    "load_test": {
        "users": 500,
        "spawn_rate": 25,
        "run_time": "10m",
        "description": "Normal load simulation"
    },
    "stress_test": {
        "users": 1500,
        "spawn_rate": 100,
        "run_time": "15m",
        "description": "High load stress test"
    },
    "spike_test": {
        "users": 2000,
        "spawn_rate": 200,
        "run_time": "5m",
        "description": "Sudden traffic spike"
    },
    "endurance_test": {
        "users": 300,
        "spawn_rate": 10,
        "run_time": "60m",
        "description": "Long duration stability test"
    },
    "breakpoint_test": {
        "users": 5000,
        "spawn_rate": 500,
        "run_time": "20m",
        "description": "Find system breaking point"
    }
}

# Performance thresholds
THRESHOLDS = {
    "response_time_p95": 500,  # ms
    "response_time_p99": 1000,  # ms
    "error_rate": 0.01,  # 1%
    "throughput_min": 100,  # requests/sec
}
