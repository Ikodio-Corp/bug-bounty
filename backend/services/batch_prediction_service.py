"""
Batch Prediction Service
Handles bulk scan predictions with optimizations for throughput
"""
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.models.bug import Bug
from backend.models.user import Scan
from backend.services.ml_prediction_optimizer import ml_prediction_optimizer, PredictionResult
from backend.core.database import get_async_db

logger = logging.getLogger(__name__)


class BatchStatus(str, Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class BatchPredictionJob:
    """Batch prediction job metadata"""
    job_id: str
    scan_id: int
    total_items: int
    processed_items: int
    successful_predictions: int
    failed_predictions: int
    status: BatchStatus
    start_time: datetime
    end_time: Optional[datetime]
    total_time_ms: float
    avg_time_per_item_ms: float
    

class BatchPredictionService:
    """
    Service for bulk prediction processing
    - Processes large batches efficiently
    - Progress tracking and reporting
    - Error handling and recovery
    - Automatic batching optimization
    """
    
    def __init__(self):
        self.optimal_batch_size = 32  # Based on testing
        self.max_concurrent_batches = 4
        self.max_retries = 3
        
        logger.info("BatchPredictionService initialized")
    
    async def _extract_features_from_bug(self, bug: Bug) -> Dict[str, Any]:
        """Extract ML features from bug data"""
        # This should match your feature extraction logic
        return {
            'title_length': len(bug.title or ''),
            'description_length': len(bug.description or ''),
            'severity': bug.severity or 'medium',
            'url': bug.url or '',
            'has_proof': bool(bug.proof_of_concept),
            'reporter_reputation': 0.5,  # Would come from user stats
            'asset_count': 1,
            'endpoint_count': 1,
            'parameter_count': 0,
            'has_headers': False,
            'has_cookies': False,
            'has_authentication': False,
            'has_ssl': 'https' in (bug.url or '').lower(),
            'response_time_ms': 0,
            'status_code': 0,
            'content_type': 'text/html',
            'response_size_bytes': 0,
            'vulnerability_pattern_match': False,
            'sql_injection_score': 0.0,
            'xss_score': 0.0,
            'csrf_score': 0.0,
            'idor_score': 0.0,
            'title_sentiment': 0.0,
            'description_sentiment': 0.0,
            'technical_detail_score': 0.5,
            'exploit_complexity': 0.5,
            'impact_score': 0.5,
        }
    
    async def predict_for_scan_bulk(
        self,
        scan_id: int,
        db: AsyncSession,
        progress_callback: Optional[callable] = None
    ) -> BatchPredictionJob:
        """
        Process all bugs in a scan with batch predictions
        
        Args:
            scan_id: Scan ID to process
            db: Database session
            progress_callback: Optional callback for progress updates
            
        Returns:
            BatchPredictionJob with results
        """
        job_id = f"batch_{scan_id}_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            # Get all bugs for scan
            result = await db.execute(
                select(Bug).where(Bug.scan_id == scan_id)
            )
            bugs = result.scalars().all()
            
            if not bugs:
                return BatchPredictionJob(
                    job_id=job_id,
                    scan_id=scan_id,
                    total_items=0,
                    processed_items=0,
                    successful_predictions=0,
                    failed_predictions=0,
                    status=BatchStatus.COMPLETED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    total_time_ms=0.0,
                    avg_time_per_item_ms=0.0
                )
            
            total_items = len(bugs)
            logger.info(f"Starting batch prediction for scan {scan_id} with {total_items} items")
            
            # Extract features for all bugs
            features_list = []
            bug_ids = []
            for bug in bugs:
                features = await self._extract_features_from_bug(bug)
                features_list.append(features)
                bug_ids.append(bug.id)
            
            # Process in optimal batches
            all_predictions = []
            processed = 0
            successful = 0
            failed = 0
            
            for i in range(0, len(features_list), self.optimal_batch_size):
                batch_features = features_list[i:i + self.optimal_batch_size]
                batch_bug_ids = bug_ids[i:i + self.optimal_batch_size]
                
                try:
                    # Batch predict
                    predictions = await ml_prediction_optimizer.predict_batch_optimized(
                        batch_features,
                        use_cache=True
                    )
                    
                    all_predictions.extend(predictions)
                    
                    # Update bugs with predictions
                    for bug_id, prediction in zip(batch_bug_ids, predictions):
                        if prediction:
                            await db.execute(
                                update(Bug)
                                .where(Bug.id == bug_id)
                                .values(
                                    ml_predicted_vulnerability=prediction.is_vulnerability,
                                    ml_predicted_type=prediction.vulnerability_type,
                                    ml_predicted_severity=prediction.severity,
                                    ml_confidence_score=prediction.confidence,
                                    ml_predicted_at=datetime.now()
                                )
                            )
                            successful += 1
                        else:
                            failed += 1
                    
                    processed += len(batch_features)
                    
                    # Progress callback
                    if progress_callback:
                        progress = (processed / total_items) * 100
                        await progress_callback(job_id, processed, total_items, progress)
                    
                    logger.info(
                        f"Batch {i // self.optimal_batch_size + 1}: "
                        f"Processed {processed}/{total_items} ({processed/total_items*100:.1f}%)"
                    )
                    
                except Exception as e:
                    logger.error(f"Batch prediction error: {e}")
                    failed += len(batch_features)
                    processed += len(batch_features)
            
            # Commit all updates
            await db.commit()
            
            # Update scan stats
            avg_confidence = sum(p.confidence for p in all_predictions if p) / len(all_predictions)
            high_confidence_count = sum(1 for p in all_predictions if p and p.confidence > 0.8)
            predicted_vulns = sum(1 for p in all_predictions if p and p.is_vulnerability)
            
            await db.execute(
                update(Scan)
                .where(Scan.id == scan_id)
                .values(
                    ml_predicted_vulnerabilities=predicted_vulns,
                    ml_confidence_average=avg_confidence,
                    ml_high_confidence_count=high_confidence_count,
                    ml_predicted_at=datetime.now()
                )
            )
            await db.commit()
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000
            avg_time = total_time / total_items if total_items > 0 else 0
            
            status = BatchStatus.COMPLETED if failed == 0 else (
                BatchStatus.PARTIAL if successful > 0 else BatchStatus.FAILED
            )
            
            job = BatchPredictionJob(
                job_id=job_id,
                scan_id=scan_id,
                total_items=total_items,
                processed_items=processed,
                successful_predictions=successful,
                failed_predictions=failed,
                status=status,
                start_time=start_time,
                end_time=end_time,
                total_time_ms=total_time,
                avg_time_per_item_ms=avg_time
            )
            
            logger.info(
                f"Batch prediction completed: {successful}/{total_items} successful, "
                f"{failed} failed, {total_time:.0f}ms total ({avg_time:.2f}ms per item)"
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Batch prediction job error: {e}")
            return BatchPredictionJob(
                job_id=job_id,
                scan_id=scan_id,
                total_items=0,
                processed_items=0,
                successful_predictions=0,
                failed_predictions=0,
                status=BatchStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                total_time_ms=0.0,
                avg_time_per_item_ms=0.0
            )
    
    async def predict_for_multiple_scans(
        self,
        scan_ids: List[int],
        db: AsyncSession
    ) -> List[BatchPredictionJob]:
        """
        Process multiple scans concurrently
        
        Args:
            scan_ids: List of scan IDs to process
            db: Database session
            
        Returns:
            List of BatchPredictionJobs
        """
        logger.info(f"Processing {len(scan_ids)} scans concurrently")
        
        # Create tasks for concurrent processing
        tasks = []
        for scan_id in scan_ids:
            task = self.predict_for_scan_bulk(scan_id, db)
            tasks.append(task)
        
        # Process with concurrency limit
        results = []
        for i in range(0, len(tasks), self.max_concurrent_batches):
            batch_tasks = tasks[i:i + self.max_concurrent_batches]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Concurrent batch error: {result}")
                else:
                    results.append(result)
        
        logger.info(f"Completed processing {len(results)} scans")
        return results
    
    async def reprocess_failed_predictions(
        self,
        scan_id: int,
        db: AsyncSession
    ) -> BatchPredictionJob:
        """
        Retry predictions for bugs that failed or have no ML prediction
        
        Args:
            scan_id: Scan ID to reprocess
            db: Database session
            
        Returns:
            BatchPredictionJob with results
        """
        # Get bugs without ML predictions
        result = await db.execute(
            select(Bug).where(
                Bug.scan_id == scan_id,
                Bug.ml_predicted_vulnerability.is_(None)
            )
        )
        bugs = result.scalars().all()
        
        if not bugs:
            logger.info(f"No failed predictions to reprocess for scan {scan_id}")
            return BatchPredictionJob(
                job_id=f"reprocess_{scan_id}_{int(time.time())}",
                scan_id=scan_id,
                total_items=0,
                processed_items=0,
                successful_predictions=0,
                failed_predictions=0,
                status=BatchStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_time_ms=0.0,
                avg_time_per_item_ms=0.0
            )
        
        logger.info(f"Reprocessing {len(bugs)} failed predictions for scan {scan_id}")
        return await self.predict_for_scan_bulk(scan_id, db)


# Global instance
batch_prediction_service = BatchPredictionService()
