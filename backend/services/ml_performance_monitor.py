"""
ML Performance Monitoring Service
Tracks inference speed, cache performance, and model health
"""
import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from prometheus_client import Counter, Histogram, Gauge, Summary

from backend.models.ml_training import MLModelMonitoring
from backend.services.ml_prediction_optimizer import ml_prediction_optimizer

logger = logging.getLogger(__name__)


# Prometheus metrics
ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total number of ML predictions',
    ['model_version', 'cached']
)

ml_inference_duration_seconds = Histogram(
    'ml_inference_duration_seconds',
    'ML inference duration in seconds',
    ['model_version', 'cached'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

ml_cache_hit_rate = Gauge(
    'ml_cache_hit_rate',
    'ML prediction cache hit rate percentage'
)

ml_batch_size = Histogram(
    'ml_batch_size',
    'ML batch prediction size',
    buckets=[1, 5, 10, 20, 32, 50, 100, 200]
)

ml_errors_total = Counter(
    'ml_errors_total',
    'Total number of ML prediction errors',
    ['error_type']
)

ml_circuit_breaker_status = Gauge(
    'ml_circuit_breaker_status',
    'ML circuit breaker status (0=closed, 1=open)'
)

ml_model_accuracy = Gauge(
    'ml_model_accuracy',
    'ML model accuracy over time window',
    ['model_version', 'time_window']
)

ml_latency_p50 = Gauge(
    'ml_latency_p50',
    'ML prediction latency 50th percentile'
)

ml_latency_p95 = Gauge(
    'ml_latency_p95',
    'ML prediction latency 95th percentile'
)

ml_latency_p99 = Gauge(
    'ml_latency_p99',
    'ML prediction latency 99th percentile'
)


class PerformanceMetric(str, Enum):
    """Performance metric types"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ACCURACY = "accuracy"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"


@dataclass
class PerformanceSnapshot:
    """Performance metrics snapshot"""
    timestamp: datetime
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_per_sec: float
    cache_hit_rate: float
    error_rate: float
    total_predictions: int
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class MLPerformanceMonitor:
    """
    Monitors ML service performance and health
    - Real-time latency tracking
    - Cache performance monitoring
    - Error rate tracking
    - Throughput measurement
    - Prometheus metrics export
    """
    
    def __init__(self):
        self.window_size = 1000  # Track last 1000 predictions
        self.latency_window = deque(maxlen=self.window_size)
        self.error_window = deque(maxlen=self.window_size)
        
        self.start_time = time.time()
        self.total_predictions = 0
        self.total_errors = 0
        
        # Performance thresholds
        self.latency_threshold_ms = 100
        self.error_rate_threshold = 0.05  # 5%
        self.cache_hit_rate_threshold = 0.70  # 70%
        
        logger.info("MLPerformanceMonitor initialized")
    
    def record_prediction(
        self,
        latency_ms: float,
        cached: bool,
        model_version: str = "v1.0",
        success: bool = True,
        error_type: Optional[str] = None
    ):
        """Record a prediction event"""
        self.total_predictions += 1
        self.latency_window.append(latency_ms)
        
        # Prometheus metrics
        ml_predictions_total.labels(
            model_version=model_version,
            cached=str(cached)
        ).inc()
        
        ml_inference_duration_seconds.labels(
            model_version=model_version,
            cached=str(cached)
        ).observe(latency_ms / 1000.0)
        
        if not success:
            self.total_errors += 1
            self.error_window.append(1)
            ml_errors_total.labels(error_type=error_type or "unknown").inc()
        else:
            self.error_window.append(0)
    
    def record_batch(
        self,
        batch_size: int,
        total_latency_ms: float,
        cached_count: int,
        model_version: str = "v1.0"
    ):
        """Record a batch prediction event"""
        avg_latency = total_latency_ms / batch_size
        
        for i in range(batch_size):
            cached = i < cached_count
            self.record_prediction(avg_latency, cached, model_version)
        
        ml_batch_size.observe(batch_size)
    
    async def get_current_snapshot(self) -> PerformanceSnapshot:
        """Get current performance snapshot"""
        if not self.latency_window:
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                throughput_per_sec=0.0,
                cache_hit_rate=0.0,
                error_rate=0.0,
                total_predictions=0
            )
        
        # Calculate latency percentiles
        sorted_latencies = sorted(self.latency_window)
        n = len(sorted_latencies)
        
        p50_idx = int(n * 0.50)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)
        
        avg_latency = sum(sorted_latencies) / n
        p50_latency = sorted_latencies[p50_idx]
        p95_latency = sorted_latencies[p95_idx]
        p99_latency = sorted_latencies[p99_idx]
        
        # Update Prometheus gauges
        ml_latency_p50.set(p50_latency)
        ml_latency_p95.set(p95_latency)
        ml_latency_p99.set(p99_latency)
        
        # Calculate throughput
        elapsed_time = time.time() - self.start_time
        throughput = self.total_predictions / elapsed_time if elapsed_time > 0 else 0.0
        
        # Calculate error rate
        error_rate = (
            sum(self.error_window) / len(self.error_window)
            if self.error_window else 0.0
        )
        
        # Get cache stats
        cache_stats = await ml_prediction_optimizer.get_cache_stats()
        cache_hit_rate = cache_stats.hit_rate / 100.0
        
        # Update Prometheus gauge
        ml_cache_hit_rate.set(cache_hit_rate * 100)
        
        return PerformanceSnapshot(
            timestamp=datetime.now(),
            avg_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            throughput_per_sec=throughput,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate,
            total_predictions=self.total_predictions
        )
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check service health against thresholds
        
        Returns:
            Health status dict with warnings
        """
        snapshot = await self.get_current_snapshot()
        cache_stats = await ml_prediction_optimizer.get_cache_stats()
        
        warnings = []
        is_healthy = True
        
        # Check latency
        if snapshot.p95_latency_ms > self.latency_threshold_ms:
            warnings.append(
                f"P95 latency ({snapshot.p95_latency_ms:.2f}ms) exceeds threshold "
                f"({self.latency_threshold_ms}ms)"
            )
            is_healthy = False
        
        # Check error rate
        if snapshot.error_rate > self.error_rate_threshold:
            warnings.append(
                f"Error rate ({snapshot.error_rate*100:.2f}%) exceeds threshold "
                f"({self.error_rate_threshold*100:.2f}%)"
            )
            is_healthy = False
        
        # Check cache performance
        if snapshot.cache_hit_rate < self.cache_hit_rate_threshold:
            warnings.append(
                f"Cache hit rate ({snapshot.cache_hit_rate*100:.1f}%) below threshold "
                f"({self.cache_hit_rate_threshold*100:.1f}%)"
            )
        
        # Check circuit breaker
        circuit_open = ml_prediction_optimizer._check_circuit_breaker()
        ml_circuit_breaker_status.set(1 if circuit_open else 0)
        
        if circuit_open:
            warnings.append("ML service circuit breaker is OPEN")
            is_healthy = False
        
        return {
            'healthy': is_healthy,
            'timestamp': datetime.now().isoformat(),
            'warnings': warnings,
            'metrics': snapshot.to_dict(),
            'cache_stats': {
                'hit_rate': cache_stats.hit_rate,
                'total_requests': cache_stats.total_requests,
                'cache_hits': cache_stats.cache_hits,
                'cache_misses': cache_stats.cache_misses,
                'avg_inference_time_ms': cache_stats.avg_inference_time_ms,
                'avg_cached_time_ms': cache_stats.avg_cached_time_ms
            },
            'circuit_breaker': {
                'open': circuit_open,
                'consecutive_failures': ml_prediction_optimizer.consecutive_failures,
                'max_failures': ml_prediction_optimizer.max_failures
            }
        }
    
    async def store_monitoring_data(
        self,
        db: AsyncSession,
        model_id: int,
        model_version: str
    ):
        """Store monitoring data to database"""
        snapshot = await self.get_current_snapshot()
        cache_stats = await ml_prediction_optimizer.get_cache_stats()
        
        monitoring_record = MLModelMonitoring(
            model_id=model_id,
            model_version=model_version,
            timestamp=snapshot.timestamp,
            prediction_count=snapshot.total_predictions,
            avg_latency_ms=snapshot.avg_latency_ms,
            p50_latency_ms=snapshot.p50_latency_ms,
            p95_latency_ms=snapshot.p95_latency_ms,
            p99_latency_ms=snapshot.p99_latency_ms,
            throughput_per_sec=snapshot.throughput_per_sec,
            cache_hit_rate=snapshot.cache_hit_rate,
            cache_miss_rate=1.0 - snapshot.cache_hit_rate,
            error_rate=snapshot.error_rate,
            memory_usage_mb=0.0,  # Would need psutil
            cpu_usage_percent=0.0,  # Would need psutil
            alerts_triggered=[],
            additional_metrics={}
        )
        
        db.add(monitoring_record)
        await db.commit()
        
        logger.info(f"Stored monitoring data for model {model_version}")
    
    async def get_performance_trend(
        self,
        db: AsyncSession,
        model_version: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get performance trend over time"""
        since = datetime.now() - timedelta(hours=hours)
        
        result = await db.execute(
            select(MLModelMonitoring)
            .where(
                and_(
                    MLModelMonitoring.model_version == model_version,
                    MLModelMonitoring.timestamp >= since
                )
            )
            .order_by(MLModelMonitoring.timestamp)
        )
        
        records = result.scalars().all()
        
        return [
            {
                'timestamp': r.timestamp.isoformat(),
                'avg_latency_ms': r.avg_latency_ms,
                'p95_latency_ms': r.p95_latency_ms,
                'throughput_per_sec': r.throughput_per_sec,
                'cache_hit_rate': r.cache_hit_rate,
                'error_rate': r.error_rate
            }
            for r in records
        ]
    
    def reset_metrics(self):
        """Reset all metrics (for testing or reset)"""
        self.latency_window.clear()
        self.error_window.clear()
        self.start_time = time.time()
        self.total_predictions = 0
        self.total_errors = 0
        logger.info("Performance metrics reset")


# Global instance
ml_performance_monitor = MLPerformanceMonitor()
