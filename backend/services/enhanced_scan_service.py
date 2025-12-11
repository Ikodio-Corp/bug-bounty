"""
Enhanced scan service with ML integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.models.bug import Scan, Bug
from backend.integrations.ml_client import ml_client, MLClientError
from backend.utils.cache import cache_result
from backend.utils.query_optimizer import QueryOptimizer
from backend.core.logging import setup_logging

logger = setup_logging()


class EnhancedScanService:
    """
    Enhanced scan service with ML prediction integration
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.optimizer = QueryOptimizer(db)
    
    async def create_scan_with_ml(
        self,
        user_id: int,
        target_url: str,
        scan_type: str,
        target_platform: Optional[str] = None,
        enable_ml: bool = True
    ) -> Scan:
        """
        Create new scan with ML prediction enabled
        
        Args:
            user_id: User ID
            target_url: Target URL to scan
            scan_type: Type of scan
            target_platform: Optional platform
            enable_ml: Enable ML predictions
            
        Returns:
            Created scan object
        """
        try:
            scan = Scan(
                user_id=user_id,
                target_url=target_url,
                target_domain=self._extract_domain(target_url),
                scan_type=scan_type,
                status="queued",
                ml_prediction_enabled=enable_ml,
                start_time=datetime.utcnow()
            )
            
            self.db.add(scan)
            await self.db.commit()
            await self.db.refresh(scan)
            
            logger.info(f"Scan created: {scan.id} for {target_url}")
            
            return scan
            
        except Exception as e:
            logger.error(f"Error creating scan: {e}")
            await self.db.rollback()
            raise
    
    async def add_ml_predictions_to_scan(
        self,
        scan_id: int,
        scan_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add ML predictions to scan results
        
        Args:
            scan_id: Scan ID
            scan_results: Original scan results
            
        Returns:
            Enhanced results with ML predictions
        """
        try:
            scan = await self.get_scan_by_id(scan_id)
            
            if not scan or not scan.ml_prediction_enabled:
                return scan_results
            
            vulnerabilities = scan_results.get("vulnerabilities", [])
            
            if not vulnerabilities:
                return scan_results
            
            logger.info(f"Processing ML predictions for scan {scan_id} with {len(vulnerabilities)} findings")
            
            ml_start = datetime.utcnow()
            predictions = []
            
            for vuln in vulnerabilities:
                scan_data = {
                    "url": vuln.get("url", scan.target_url),
                    "method": vuln.get("method", "GET"),
                    "payload": vuln.get("payload", ""),
                    "headers": vuln.get("headers", {}),
                    "response_code": vuln.get("response_code", 200),
                    "response_body": vuln.get("response_body", ""),
                    "response_time_ms": vuln.get("response_time", 0)
                }
                
                prediction = await ml_client.predict_vulnerability(scan_data)
                
                if prediction and not prediction.get("error"):
                    vuln["ml_prediction"] = {
                        "is_vulnerability": prediction.get("is_vulnerability"),
                        "confidence": prediction.get("confidence"),
                        "vulnerability_type": prediction.get("vulnerability_type"),
                        "severity_score": prediction.get("severity_score"),
                        "prediction_id": prediction.get("prediction_id")
                    }
                    predictions.append(prediction)
            
            ml_duration = int((datetime.utcnow() - ml_start).total_seconds() * 1000)
            
            # Calculate statistics
            high_confidence_predictions = [
                p for p in predictions 
                if p.get("confidence", 0) >= 0.7
            ]
            
            avg_confidence = (
                sum(p.get("confidence", 0) for p in predictions) / len(predictions)
                if predictions else 0.0
            )
            
            # Update scan with ML metadata
            scan.ml_predicted_vulnerabilities = len(predictions)
            scan.ml_confidence_average = avg_confidence
            scan.ml_high_confidence_count = len(high_confidence_predictions)
            scan.ml_prediction_time_ms = ml_duration
            scan.ml_predictions_data = {
                "predictions": predictions,
                "statistics": {
                    "total": len(predictions),
                    "high_confidence": len(high_confidence_predictions),
                    "average_confidence": avg_confidence
                }
            }
            scan.ml_predicted_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"ML predictions completed for scan {scan_id}: "
                       f"{len(high_confidence_predictions)}/{len(predictions)} high confidence")
            
            # Add ML summary to results
            scan_results["ml_analysis"] = {
                "enabled": True,
                "predictions_count": len(predictions),
                "high_confidence_count": len(high_confidence_predictions),
                "average_confidence": round(avg_confidence, 4),
                "processing_time_ms": ml_duration
            }
            
            return scan_results
            
        except MLClientError as e:
            logger.error(f"ML prediction failed for scan {scan_id}: {e}")
            scan_results["ml_analysis"] = {
                "enabled": True,
                "error": str(e),
                "fallback_mode": True
            }
            return scan_results
        except Exception as e:
            logger.error(f"Error adding ML predictions: {e}")
            return scan_results
    
    async def process_scan_with_ml(
        self,
        scan_id: int,
        raw_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process scan results with ML enhancement
        
        Args:
            scan_id: Scan ID
            raw_results: Raw scan results
            
        Returns:
            Processed results with ML predictions
        """
        try:
            # Add ML predictions
            enhanced_results = await self.add_ml_predictions_to_scan(
                scan_id,
                raw_results
            )
            
            # Filter high confidence findings
            vulnerabilities = enhanced_results.get("vulnerabilities", [])
            high_confidence_vulns = [
                v for v in vulnerabilities
                if v.get("ml_prediction", {}).get("confidence", 0) >= 0.7
            ]
            
            enhanced_results["high_confidence_vulnerabilities"] = high_confidence_vulns
            enhanced_results["confidence_distribution"] = self._calculate_confidence_distribution(
                vulnerabilities
            )
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error processing scan with ML: {e}")
            return raw_results
    
    def _calculate_confidence_distribution(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate confidence score distribution"""
        distribution = {
            "very_high": 0,  # >= 0.9
            "high": 0,       # 0.7-0.89
            "medium": 0,     # 0.5-0.69
            "low": 0,        # < 0.5
            "no_prediction": 0
        }
        
        for vuln in vulnerabilities:
            ml_pred = vuln.get("ml_prediction")
            if not ml_pred:
                distribution["no_prediction"] += 1
                continue
            
            confidence = ml_pred.get("confidence", 0)
            
            if confidence >= 0.9:
                distribution["very_high"] += 1
            elif confidence >= 0.7:
                distribution["high"] += 1
            elif confidence >= 0.5:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    async def submit_ml_feedback_for_bug(
        self,
        bug_id: int,
        is_correct: bool,
        actual_label: Optional[bool] = None,
        feedback_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit ML feedback for a bug
        
        Args:
            bug_id: Bug ID
            is_correct: Whether ML prediction was correct
            actual_label: Actual vulnerability label
            feedback_notes: Additional notes
            
        Returns:
            Feedback submission result
        """
        try:
            # Get bug with ML prediction
            result = await self.db.execute(
                select(Bug).where(Bug.id == bug_id)
            )
            bug = result.scalar_one_or_none()
            
            if not bug:
                raise ValueError(f"Bug {bug_id} not found")
            
            if not bug.ml_prediction_id:
                raise ValueError(f"Bug {bug_id} has no ML prediction")
            
            # Submit feedback to ML service
            feedback_result = await ml_client.submit_feedback(
                prediction_id=bug.ml_prediction_id,
                is_correct=is_correct,
                actual_label=actual_label,
                feedback_notes=feedback_notes
            )
            
            # Update bug with feedback
            bug.ml_prediction_feedback = "correct" if is_correct else "incorrect"
            bug.ml_feedback_notes = feedback_notes
            
            await self.db.commit()
            
            logger.info(f"ML feedback submitted for bug {bug_id}")
            
            return feedback_result
            
        except Exception as e:
            logger.error(f"Error submitting ML feedback: {e}")
            raise
    
    async def get_ml_statistics(
        self,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get ML prediction statistics
        
        Args:
            user_id: Optional user ID filter
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        try:
            # Build query
            query = select(Scan).where(
                Scan.ml_prediction_enabled == True,
                Scan.ml_predicted_at != None
            )
            
            if user_id:
                query = query.where(Scan.user_id == user_id)
            
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.where(Scan.ml_predicted_at >= cutoff_date)
            
            result = await self.db.execute(query)
            scans = result.scalars().all()
            
            if not scans:
                return {
                    "total_scans": 0,
                    "total_predictions": 0,
                    "average_confidence": 0.0
                }
            
            total_predictions = sum(s.ml_predicted_vulnerabilities or 0 for s in scans)
            total_high_confidence = sum(s.ml_high_confidence_count or 0 for s in scans)
            avg_confidence = sum(s.ml_confidence_average or 0 for s in scans) / len(scans)
            avg_processing_time = sum(s.ml_prediction_time_ms or 0 for s in scans) / len(scans)
            
            return {
                "total_scans": len(scans),
                "total_predictions": total_predictions,
                "high_confidence_predictions": total_high_confidence,
                "average_confidence": round(avg_confidence, 4),
                "average_processing_time_ms": round(avg_processing_time, 2),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting ML statistics: {e}")
            return {"error": str(e)}
    
    @cache_result(ttl=180, key_prefix="scan")
    async def get_scan_by_id(self, scan_id: int) -> Optional[Scan]:
        """Get scan by ID with caching"""
        result = await self.db.execute(
            select(Scan).where(Scan.id == scan_id)
        )
        return result.scalar_one_or_none()
    
    async def update_scan_status(
        self,
        scan_id: int,
        status: str,
        results: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> Optional[Scan]:
        """Update scan status and results"""
        try:
            scan = await self.get_scan_by_id(scan_id)
            
            if not scan:
                return None
            
            scan.status = status
            
            if results:
                scan.vulnerabilities_found = len(results.get("vulnerabilities", []))
                scan.scan_metadata = results
            
            if error_message:
                scan.error_message = error_message
                scan.success = False
            elif status == "completed":
                scan.success = True
                scan.end_time = datetime.utcnow()
                if scan.start_time:
                    scan.duration_seconds = int(
                        (scan.end_time - scan.start_time).total_seconds()
                    )
            
            await self.db.commit()
            await self.db.refresh(scan)
            
            return scan
            
        except Exception as e:
            logger.error(f"Error updating scan status: {e}")
            await self.db.rollback()
            raise
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or url
