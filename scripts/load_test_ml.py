#!/usr/bin/env python3
"""
ML Performance Load Testing Script
Tests ML prediction service under various load conditions
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json
import sys

# Test configuration
BASE_URL = "http://localhost:8000"
ML_ENDPOINT = f"{BASE_URL}/api/ml/predict"
BATCH_ENDPOINT = f"{BASE_URL}/api/ml/predict/batch"

# Sample test data
SAMPLE_FEATURES = {
    'title_length': 45,
    'description_length': 320,
    'severity': 'high',
    'url': 'https://example.com/api/endpoint',
    'has_proof': True,
    'reporter_reputation': 0.85,
    'asset_count': 3,
    'endpoint_count': 5,
    'parameter_count': 4,
    'has_headers': True,
    'has_cookies': True,
    'has_authentication': True,
    'has_ssl': True,
    'response_time_ms': 250,
    'status_code': 200,
    'content_type': 'application/json',
    'response_size_bytes': 4096,
    'vulnerability_pattern_match': True,
    'sql_injection_score': 0.75,
    'xss_score': 0.35,
    'csrf_score': 0.20,
    'idor_score': 0.45,
    'title_sentiment': -0.15,
    'description_sentiment': -0.25,
    'technical_detail_score': 0.82,
    'exploit_complexity': 0.60,
    'impact_score': 0.75,
}


class LoadTestResults:
    """Store and analyze load test results"""
    
    def __init__(self):
        self.latencies: List[float] = []
        self.errors: List[str] = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()
        self.end_time = None
    
    def record_success(self, latency_ms: float):
        """Record successful request"""
        self.latencies.append(latency_ms)
        self.successful_requests += 1
    
    def record_error(self, error: str):
        """Record failed request"""
        self.errors.append(error)
        self.failed_requests += 1
    
    def finalize(self):
        """Finalize results"""
        self.end_time = time.time()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate statistics"""
        if not self.latencies:
            return {
                'total_requests': self.successful_requests + self.failed_requests,
                'successful_requests': self.successful_requests,
                'failed_requests': self.failed_requests,
                'error_rate': 1.0 if self.failed_requests > 0 else 0.0,
                'total_duration_sec': self.end_time - self.start_time if self.end_time else 0,
                'throughput_per_sec': 0.0,
                'avg_latency_ms': 0.0,
                'min_latency_ms': 0.0,
                'max_latency_ms': 0.0,
                'p50_latency_ms': 0.0,
                'p95_latency_ms': 0.0,
                'p99_latency_ms': 0.0,
            }
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        total_duration = self.end_time - self.start_time if self.end_time else 0
        total_requests = self.successful_requests + self.failed_requests
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'error_rate': self.failed_requests / total_requests if total_requests > 0 else 0.0,
            'total_duration_sec': total_duration,
            'throughput_per_sec': total_requests / total_duration if total_duration > 0 else 0.0,
            'avg_latency_ms': statistics.mean(self.latencies),
            'min_latency_ms': min(self.latencies),
            'max_latency_ms': max(self.latencies),
            'p50_latency_ms': sorted_latencies[int(n * 0.50)],
            'p95_latency_ms': sorted_latencies[int(n * 0.95)],
            'p99_latency_ms': sorted_latencies[int(n * 0.99)],
            'std_dev_ms': statistics.stdev(self.latencies) if n > 1 else 0.0,
        }


async def single_prediction_request(session: aiohttp.ClientSession, features: Dict[str, Any]) -> float:
    """Make a single prediction request"""
    start = time.time()
    
    try:
        async with session.post(ML_ENDPOINT, json={'features': features}) as response:
            await response.json()
            latency = (time.time() - start) * 1000
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            
            return latency
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


async def batch_prediction_request(
    session: aiohttp.ClientSession,
    features_list: List[Dict[str, Any]]
) -> float:
    """Make a batch prediction request"""
    start = time.time()
    
    try:
        async with session.post(BATCH_ENDPOINT, json={'features_list': features_list}) as response:
            await response.json()
            latency = (time.time() - start) * 1000
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            
            return latency
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


async def concurrent_load_test(
    num_requests: int,
    concurrency: int,
    features: Dict[str, Any]
) -> LoadTestResults:
    """
    Run concurrent load test
    
    Args:
        num_requests: Total number of requests
        concurrency: Number of concurrent requests
        features: Feature data for prediction
    """
    print(f"\n=== Concurrent Load Test ===")
    print(f"Total requests: {num_requests}")
    print(f"Concurrency: {concurrency}")
    print(f"Target: <100ms per request")
    print(f"Starting at {datetime.now().isoformat()}")
    
    results = LoadTestResults()
    
    async with aiohttp.ClientSession() as session:
        # Create task queue
        tasks = []
        for i in range(num_requests):
            task = single_prediction_request(session, features)
            tasks.append(task)
        
        # Execute with concurrency limit
        for i in range(0, len(tasks), concurrency):
            batch_tasks = tasks[i:i + concurrency]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.record_error(str(result))
                else:
                    results.record_success(result)
            
            # Progress indicator
            progress = (i + len(batch_tasks)) / num_requests * 100
            print(f"Progress: {progress:.1f}% ({i + len(batch_tasks)}/{num_requests})", end='\r')
        
        print()  # New line after progress
    
    results.finalize()
    return results


async def sustained_load_test(
    duration_seconds: int,
    requests_per_second: int,
    features: Dict[str, Any]
) -> LoadTestResults:
    """
    Run sustained load test for specified duration
    
    Args:
        duration_seconds: Test duration in seconds
        requests_per_second: Target RPS
        features: Feature data for prediction
    """
    print(f"\n=== Sustained Load Test ===")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Target RPS: {requests_per_second}")
    print(f"Starting at {datetime.now().isoformat()}")
    
    results = LoadTestResults()
    interval = 1.0 / requests_per_second
    end_time = time.time() + duration_seconds
    
    async with aiohttp.ClientSession() as session:
        request_count = 0
        
        while time.time() < end_time:
            start = time.time()
            
            try:
                latency = await single_prediction_request(session, features)
                results.record_success(latency)
            except Exception as e:
                results.record_error(str(e))
            
            request_count += 1
            
            # Progress indicator
            elapsed = time.time() - results.start_time
            print(f"Elapsed: {elapsed:.1f}s | Requests: {request_count} | RPS: {request_count/elapsed:.1f}", end='\r')
            
            # Sleep to maintain target RPS
            elapsed_request = time.time() - start
            sleep_time = max(0, interval - elapsed_request)
            await asyncio.sleep(sleep_time)
        
        print()  # New line after progress
    
    results.finalize()
    return results


async def batch_load_test(
    num_batches: int,
    batch_size: int,
    features: Dict[str, Any]
) -> LoadTestResults:
    """
    Test batch prediction performance
    
    Args:
        num_batches: Number of batches to send
        batch_size: Size of each batch
        features: Feature data template
    """
    print(f"\n=== Batch Load Test ===")
    print(f"Number of batches: {num_batches}")
    print(f"Batch size: {batch_size}")
    print(f"Total predictions: {num_batches * batch_size}")
    print(f"Starting at {datetime.now().isoformat()}")
    
    results = LoadTestResults()
    
    async with aiohttp.ClientSession() as session:
        for i in range(num_batches):
            # Create batch with slight variations
            features_list = []
            for j in range(batch_size):
                feature_copy = features.copy()
                feature_copy['title_length'] = features['title_length'] + j
                features_list.append(feature_copy)
            
            try:
                latency = await batch_prediction_request(session, features_list)
                # Record per-item latency
                per_item_latency = latency / batch_size
                for _ in range(batch_size):
                    results.record_success(per_item_latency)
            except Exception as e:
                for _ in range(batch_size):
                    results.record_error(str(e))
            
            # Progress indicator
            progress = (i + 1) / num_batches * 100
            print(f"Progress: {progress:.1f}% ({i + 1}/{num_batches} batches)", end='\r')
        
        print()  # New line after progress
    
    results.finalize()
    return results


def print_results(test_name: str, results: LoadTestResults):
    """Print formatted test results"""
    stats = results.get_statistics()
    
    print(f"\n{'=' * 60}")
    print(f"Test: {test_name}")
    print(f"{'=' * 60}")
    print(f"Total Requests:       {stats['total_requests']}")
    print(f"Successful:           {stats['successful_requests']}")
    print(f"Failed:               {stats['failed_requests']}")
    print(f"Error Rate:           {stats['error_rate'] * 100:.2f}%")
    print(f"Total Duration:       {stats['total_duration_sec']:.2f}s")
    print(f"Throughput:           {stats['throughput_per_sec']:.2f} req/s")
    print(f"\nLatency Statistics:")
    print(f"  Average:            {stats['avg_latency_ms']:.2f}ms")
    print(f"  Min:                {stats['min_latency_ms']:.2f}ms")
    print(f"  Max:                {stats['max_latency_ms']:.2f}ms")
    print(f"  P50 (Median):       {stats['p50_latency_ms']:.2f}ms")
    print(f"  P95:                {stats['p95_latency_ms']:.2f}ms")
    print(f"  P99:                {stats['p99_latency_ms']:.2f}ms")
    print(f"  Std Dev:            {stats.get('std_dev_ms', 0):.2f}ms")
    
    # Performance assessment
    print(f"\nPerformance Assessment:")
    if stats['p95_latency_ms'] < 100:
        print(f"  ✓ P95 latency MEETS target (<100ms)")
    else:
        print(f"  ✗ P95 latency EXCEEDS target (target: 100ms, actual: {stats['p95_latency_ms']:.2f}ms)")
    
    if stats['error_rate'] < 0.01:
        print(f"  ✓ Error rate ACCEPTABLE (<1%)")
    else:
        print(f"  ⚠ Error rate HIGH (target: <1%, actual: {stats['error_rate'] * 100:.2f}%)")
    
    if results.errors:
        print(f"\nSample Errors (first 5):")
        for error in results.errors[:5]:
            print(f"  - {error}")


async def main():
    """Run all load tests"""
    print("=" * 60)
    print("IKODIO ML Performance Load Testing")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test started: {datetime.now().isoformat()}")
    
    # Test 1: Warm-up (cache cold start)
    print("\n--- Warm-up Test (10 requests) ---")
    warmup_results = await concurrent_load_test(10, 1, SAMPLE_FEATURES)
    print_results("Warm-up (Cold Cache)", warmup_results)
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test 2: Low concurrency (cache warm)
    results_low = await concurrent_load_test(100, 5, SAMPLE_FEATURES)
    print_results("Low Concurrency (5 concurrent)", results_low)
    
    # Test 3: Medium concurrency
    results_medium = await concurrent_load_test(200, 20, SAMPLE_FEATURES)
    print_results("Medium Concurrency (20 concurrent)", results_medium)
    
    # Test 4: High concurrency
    results_high = await concurrent_load_test(500, 50, SAMPLE_FEATURES)
    print_results("High Concurrency (50 concurrent)", results_high)
    
    # Test 5: Sustained load
    results_sustained = await sustained_load_test(60, 20, SAMPLE_FEATURES)
    print_results("Sustained Load (20 RPS for 60s)", results_sustained)
    
    # Test 6: Batch predictions
    results_batch = await batch_load_test(50, 32, SAMPLE_FEATURES)
    print_results("Batch Predictions (50 batches of 32)", results_batch)
    
    # Summary
    print(f"\n{'=' * 60}")
    print("LOAD TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Completed at: {datetime.now().isoformat()}")
    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nLoad test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nLoad test failed: {e}")
        sys.exit(1)
