"""
ML Prediction Optimizer Service
Optimizes inference speed with caching, batching, and performance monitoring
Target: <100ms inference time
"""
import time
import asyncio
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
import redis.asyncio as aioredis

from backend.core.config import settings
from backend.core.redis import get_async_redis
from backend.integrations.ml_client import ml_client
from backend.models.bug import Bug
from backend.models.user import Scan

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Optimized prediction result with metadata"""
    is_vulnerability: bool
    vulnerability_type: str
    severity: float
    confidence: float
    inference_time_ms: float
    cached: bool
    model_version: str
    features_used: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CacheStats:
    """Cache statistics"""
    hit_rate: float
    total_requests: int
    cache_hits: int
    cache_misses: int
    avg_inference_time_ms: float
    avg_cached_time_ms: float
    

class MLPredictionOptimizer:
    """
    Optimized ML prediction service with:
    - Redis caching with intelligent TTL
    - Feature hashing for cache keys
    - Batch prediction support
    - Performance monitoring
    - Circuit breaker pattern
    """
    
    def __init__(self):
        self.cache_ttl_seconds = 3600  # 1 hour default
        self.batch_size = 32
        self.max_inference_time_ms = 100  # Target
        self.cache_prefix = "ml:pred:"
        
        # Performance tracking
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_inference_time_ms = 0.0
        self.total_cached_time_ms = 0.0
        
        # Circuit breaker
        self.consecutive_failures = 0
        self.max_failures = 5
        self.circuit_open = False
        self.circuit_open_until: Optional[datetime] = None
        
        logger.info("MLPredictionOptimizer initialized")
    
    def _generate_cache_key(self, features: Dict[str, Any]) -> str:
        """
        Generate deterministic cache key from features
        Uses MD5 hash of sorted feature JSON
        """
        # Sort keys for consistency
        sorted_features = json.dumps(features, sort_keys=True)
        hash_object = hashlib.md5(sorted_features.encode())
        return f"{self.cache_prefix}{hash_object.hexdigest()}"
    
    async def _get_from_cache(
        self,
        cache_key: str,
        redis_client: aioredis.Redis
    ) -> Optional[Dict[str, Any]]:
        """Retrieve prediction from cache"""
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                self.cache_hits += 1
                return json.loads(cached_data)
            self.cache_misses += 1
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    async def _set_to_cache(
        self,
        cache_key: str,
        data: Dict[str, Any],
        redis_client: aioredis.Redis,
        ttl_seconds: Optional[int] = None
    ):
        """Store prediction in cache with TTL"""
        try:
            ttl = ttl_seconds or self.cache_ttl_seconds
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_open:
            if datetime.now() > self.circuit_open_until:
                # Reset circuit breaker
                self.circuit_open = False
                self.consecutive_failures = 0
                logger.info("Circuit breaker reset")
                return False
            return True
        return False
    
    def _record_failure(self):
        """Record prediction failure for circuit breaker"""
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_failures:
            self.circuit_open = True
            self.circuit_open_until = datetime.now() + timedelta(minutes=5)
            logger.warning(
                f"Circuit breaker opened after {self.consecutive_failures} failures. "
                f"Will retry at {self.circuit_open_until}"
            )
    
    def _record_success(self):
        """Record successful prediction"""
        if self.consecutive_failures > 0:
            self.consecutive_failures = 0
    
    async def predict_optimized(
        self,
        features: Dict[str, Any],
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ) -> PredictionResult:
        """
        Optimized single prediction with caching
        
        Args:
            features: Feature dictionary for prediction
            use_cache: Whether to use cache
            cache_ttl: Custom cache TTL in seconds
            
        Returns:
            PredictionResult with performance metrics
        """
        start_time = time.time()
        self.total_requests += 1
        cached = False
        
        # Check circuit breaker
        if self._check_circuit_breaker():
            raise RuntimeError("ML service circuit breaker is open")
        
        # Try cache first
        redis_client = await get_async_redis()
        cache_key = self._generate_cache_key(features)
        
        if use_cache:
            cached_result = await self._get_from_cache(cache_key, redis_client)
            if cached_result:
                cached_time = (time.time() - start_time) * 1000
                self.total_cached_time_ms += cached_time
                
                return PredictionResult(
                    is_vulnerability=cached_result['is_vulnerability'],
                    vulnerability_type=cached_result['vulnerability_type'],
                    severity=cached_result['severity'],
                    confidence=cached_result['confidence'],
                    inference_time_ms=cached_time,
                    cached=True,
                    model_version=cached_result.get('model_version', 'unknown'),
                    features_used=len(features)
                )
        
        # Make prediction
        try:
            prediction = await ml_client.predict(features)
            self._record_success()
            
            # Calculate inference time
            inference_time = (time.time() - start_time) * 1000
            self.total_inference_time_ms += inference_time
            
            # Prepare result
            result = PredictionResult(
                is_vulnerability=prediction.get('is_vulnerability', False),
                vulnerability_type=prediction.get('vulnerability_type', 'unknown'),
                severity=prediction.get('severity', 0.0),
                confidence=prediction.get('confidence', 0.0),
                inference_time_ms=inference_time,
                cached=False,
                model_version=prediction.get('model_version', 'v1.0'),
                features_used=len(features)
            )
            
            # Cache result
            if use_cache:
                cache_data = {
                    'is_vulnerability': result.is_vulnerability,
                    'vulnerability_type': result.vulnerability_type,
                    'severity': result.severity,
                    'confidence': result.confidence,
                    'model_version': result.model_version
                }
                await self._set_to_cache(cache_key, cache_data, redis_client, cache_ttl)
            
            # Log if exceeds target time
            if inference_time > self.max_inference_time_ms:
                logger.warning(
                    f"Inference time {inference_time:.2f}ms exceeds target "
                    f"{self.max_inference_time_ms}ms"
                )
            
            return result
            
        except Exception as e:
            self._record_failure()
            logger.error(f"Prediction error: {e}")
            raise
    
    async def predict_batch_optimized(
        self,
        features_list: List[Dict[str, Any]],
        use_cache: bool = True
    ) -> List[PredictionResult]:
        """
        Optimized batch prediction with intelligent caching
        
        Args:
            features_list: List of feature dictionaries
            use_cache: Whether to use cache
            
        Returns:
            List of PredictionResults
        """
        start_time = time.time()
        results = []
        uncached_indices = []
        uncached_features = []
        
        redis_client = await get_async_redis()
        
        # Check cache for all predictions
        if use_cache:
            for idx, features in enumerate(features_list):
                cache_key = self._generate_cache_key(features)
                cached_result = await self._get_from_cache(cache_key, redis_client)
                
                if cached_result:
                    results.append(PredictionResult(
                        is_vulnerability=cached_result['is_vulnerability'],
                        vulnerability_type=cached_result['vulnerability_type'],
                        severity=cached_result['severity'],
                        confidence=cached_result['confidence'],
                        inference_time_ms=0.0,  # Will be set later
                        cached=True,
                        model_version=cached_result.get('model_version', 'unknown'),
                        features_used=len(features)
                    ))
                else:
                    results.append(None)
                    uncached_indices.append(idx)
                    uncached_features.append(features)
        else:
            uncached_indices = list(range(len(features_list)))
            uncached_features = features_list
            results = [None] * len(features_list)
        
        # Batch predict uncached items
        if uncached_features:
            try:
                predictions = await ml_client.batch_predict(uncached_features)
                
                for idx, prediction in zip(uncached_indices, predictions):
                    features = features_list[idx]
                    
                    result = PredictionResult(
                        is_vulnerability=prediction.get('is_vulnerability', False),
                        vulnerability_type=prediction.get('vulnerability_type', 'unknown'),
                        severity=prediction.get('severity', 0.0),
                        confidence=prediction.get('confidence', 0.0),
                        inference_time_ms=0.0,  # Batch time shared
                        cached=False,
                        model_version=prediction.get('model_version', 'v1.0'),
                        features_used=len(features)
                    )
                    
                    results[idx] = result
                    
                    # Cache result
                    if use_cache:
                        cache_key = self._generate_cache_key(features)
                        cache_data = {
                            'is_vulnerability': result.is_vulnerability,
                            'vulnerability_type': result.vulnerability_type,
                            'severity': result.severity,
                            'confidence': result.confidence,
                            'model_version': result.model_version
                        }
                        await self._set_to_cache(cache_key, cache_data, redis_client)
                
                self._record_success()
                
            except Exception as e:
                self._record_failure()
                logger.error(f"Batch prediction error: {e}")
                raise
        
        # Calculate total batch time
        batch_time = (time.time() - start_time) * 1000
        avg_time_per_prediction = batch_time / len(features_list)
        
        # Update inference times
        for result in results:
            if result and not result.cached:
                result.inference_time_ms = avg_time_per_prediction
        
        logger.info(
            f"Batch prediction: {len(features_list)} items in {batch_time:.2f}ms "
            f"({avg_time_per_prediction:.2f}ms per item)"
        )
        
        return results
    
    async def get_cache_stats(self) -> CacheStats:
        """Get cache performance statistics"""
        total = self.total_requests
        if total == 0:
            return CacheStats(
                hit_rate=0.0,
                total_requests=0,
                cache_hits=0,
                cache_misses=0,
                avg_inference_time_ms=0.0,
                avg_cached_time_ms=0.0
            )
        
        hit_rate = (self.cache_hits / total) * 100
        
        avg_inference_time = (
            self.total_inference_time_ms / self.cache_misses
            if self.cache_misses > 0 else 0.0
        )
        
        avg_cached_time = (
            self.total_cached_time_ms / self.cache_hits
            if self.cache_hits > 0 else 0.0
        )
        
        return CacheStats(
            hit_rate=hit_rate,
            total_requests=total,
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses,
            avg_inference_time_ms=avg_inference_time,
            avg_cached_time_ms=avg_cached_time
        )
    
    async def clear_cache_for_model_update(self, model_version: str):
        """Clear cache when model is updated"""
        try:
            redis_client = await get_async_redis()
            # Delete all prediction cache keys
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(
                    cursor,
                    match=f"{self.cache_prefix}*",
                    count=100
                )
                if keys:
                    await redis_client.delete(*keys)
                if cursor == 0:
                    break
            
            logger.info(f"Cache cleared for model version {model_version}")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


# Global instance
ml_prediction_optimizer = MLPredictionOptimizer()
