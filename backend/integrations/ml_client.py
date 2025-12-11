"""
ML Engine Client - Interface to communicate with ML microservice
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import time

from backend.core.config import settings
from backend.core.redis import redis_client


class MLClientError(Exception):
    """Custom exception for ML client errors"""
    pass


class MLClient:
    """
    Client for interacting with ML Engine microservice
    Handles predictions, model management, and analytics
    """
    
    def __init__(self):
        self.base_url = settings.ML_ENGINE_URL
        self.timeout = httpx.Timeout(30.0, connect=5.0)
        self.cache_ttl = 300  # 5 minutes cache
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to ML service
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            json_data: Request body
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            MLClientError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params
                )
                
                if response.status_code >= 400:
                    raise MLClientError(
                        f"ML service error: {response.status_code} - {response.text}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException as e:
            raise MLClientError(f"ML service timeout: {str(e)}")
        except httpx.RequestError as e:
            raise MLClientError(f"ML service request failed: {str(e)}")
        except Exception as e:
            raise MLClientError(f"Unexpected error: {str(e)}")
    
    async def predict_vulnerability(
        self,
        scan_data: Dict[str, Any],
        model_type: str = "rule_based",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Predict if scan result contains vulnerability
        
        Args:
            scan_data: Scan data dictionary
            model_type: Model type to use
            use_cache: Whether to use cached predictions
            
        Returns:
            Prediction result with confidence score
        """
        try:
            # Check cache if enabled
            if use_cache:
                cache_key = f"ml:prediction:{hash(str(scan_data))}"
                cached = await redis_client.get(cache_key)
                if cached:
                    return cached
            
            # Make prediction request
            result = await self._make_request(
                method="POST",
                endpoint="/api/models/predict/production",
                json_data=scan_data,
                params={"model_type": model_type}
            )
            
            # Cache result
            if use_cache:
                await redis_client.set(
                    cache_key,
                    result,
                    expire=self.cache_ttl
                )
            
            return result
            
        except MLClientError as e:
            # Log error but don't fail scan
            print(f"ML prediction failed: {e}")
            return {
                "is_vulnerability": None,
                "confidence": 0.0,
                "error": str(e),
                "fallback": True
            }
    
    async def batch_predict(
        self,
        scan_data_list: List[Dict[str, Any]],
        model_type: str = "rule_based"
    ) -> List[Dict[str, Any]]:
        """
        Batch predict multiple scan results
        
        Args:
            scan_data_list: List of scan data
            model_type: Model type to use
            
        Returns:
            List of prediction results
        """
        try:
            # Make batch prediction request
            result = await self._make_request(
                method="POST",
                endpoint="/api/models/predict/batch",
                json_data={
                    "scan_data": scan_data_list,
                    "model_type": model_type
                }
            )
            
            return result.get("predictions", [])
            
            if not model:
                raise MLClientError(f"No production model found for {model_type}")
            
            result = await self._make_request(
                method="POST",
                endpoint="/api/models/predict/batch",
                json_data={
                    "model_id": model["id"],
                    "scan_data_list": scan_data_list
                }
            )
            
            return result.get("predictions", [])
            
        except MLClientError as e:
            print(f"Batch prediction failed: {e}")
            return [{"error": str(e)} for _ in scan_data_list]
    
    async def submit_feedback(
        self,
        prediction_id: int,
        is_correct: bool,
        actual_label: Optional[bool] = None,
        feedback_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback for a prediction
        
        Args:
            prediction_id: Prediction ID
            is_correct: Whether prediction was correct
            actual_label: Actual label if different
            feedback_notes: Additional notes
            
        Returns:
            Feedback submission result
        """
        try:
            return await self._make_request(
                method="POST",
                endpoint=f"/api/models/predictions/{prediction_id}/feedback",
                json_data={
                    "is_correct": is_correct,
                    "actual_label": actual_label,
                    "feedback_notes": feedback_notes
                }
            )
        except MLClientError as e:
            raise MLClientError(f"Failed to submit feedback: {e}")
    
    async def get_production_model(
        self,
        model_type: str = "rule_based"
    ) -> Optional[Dict[str, Any]]:
        """
        Get production model info
        
        Args:
            model_type: Model type
            
        Returns:
            Model info or None
        """
        try:
            # Check cache
            cache_key = f"ml:production_model:{model_type}"
            cached = await redis_client.get(cache_key)
            if cached:
                return cached
            
            # Get from API
            models = await self._make_request(
                method="GET",
                endpoint="/api/models/list",
                params={
                    "model_type": model_type,
                    "is_production": True,
                    "limit": 1
                }
            )
            
            model = models[0] if models else None
            
            # Cache for 1 hour
            if model:
                await redis_client.set(
                    cache_key,
                    model,
                    expire=3600
                )
            
            return model
            
        except MLClientError:
            return None
    
    async def get_model_statistics(
        self,
        model_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get prediction statistics
        
        Args:
            model_id: Optional model ID filter
            
        Returns:
            Statistics dictionary
        """
        try:
            params = {}
            if model_id:
                params["model_id"] = model_id
            
            return await self._make_request(
                method="GET",
                endpoint="/api/models/predictions/statistics",
                params=params
            )
        except MLClientError as e:
            return {"error": str(e)}
    
    async def get_model_drift(
        self,
        model_id: int,
        recent_predictions: int = 100
    ) -> Dict[str, Any]:
        """
        Get model drift analysis
        
        Args:
            model_id: Model ID
            recent_predictions: Number of recent predictions to analyze
            
        Returns:
            Drift analysis result
        """
        try:
            return await self._make_request(
                method="GET",
                endpoint=f"/api/models/{model_id}/drift",
                params={"recent_predictions": recent_predictions}
            )
        except MLClientError as e:
            return {"error": str(e)}
    
    async def list_models(
        self,
        model_type: Optional[str] = None,
        is_production: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List available models
        
        Args:
            model_type: Filter by model type
            is_production: Filter by production status
            limit: Maximum results
            
        Returns:
            List of models
        """
        try:
            params = {"limit": limit}
            if model_type:
                params["model_type"] = model_type
            if is_production is not None:
                params["is_production"] = is_production
            
            return await self._make_request(
                method="GET",
                endpoint="/api/models/list",
                params=params
            )
        except MLClientError as e:
            return []
    
    async def compare_models(
        self,
        model_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Compare multiple models
        
        Args:
            model_ids: List of model IDs
            
        Returns:
            Comparison results
        """
        try:
            return await self._make_request(
                method="POST",
                endpoint="/api/models/compare",
                json_data={"model_ids": model_ids}
            )
        except MLClientError as e:
            return {"error": str(e)}
    
    async def get_evaluation_report(
        self,
        model_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive evaluation report
        
        Args:
            model_id: Model ID
            
        Returns:
            Evaluation report
        """
        try:
            return await self._make_request(
                method="GET",
                endpoint=f"/api/models/{model_id}/report"
            )
        except MLClientError as e:
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """
        Check ML service health
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/health"
            )
            return result.get("status") == "healthy"
        except MLClientError:
            return False
    
    async def train_model(
        self,
        model_type: str,
        training_data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Train a new model
        
        Args:
            model_type: Type of model to train
            training_data: Training data
            config: Training configuration
            
        Returns:
            Training result with model version info
        """
        try:
            return await self._make_request(
                method="POST",
                endpoint="/api/models/train",
                json_data={
                    "model_type": model_type,
                    "training_data": training_data,
                    "config": config
                }
            )
        except MLClientError as e:
            raise MLClientError(f"Training failed: {str(e)}")
    
    async def incremental_learning(
        self,
        model_type: str,
        feedback_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform incremental learning with feedback data
        
        Args:
            model_type: Type of model
            feedback_data: Feedback data for learning
            
        Returns:
            Result of incremental learning
        """
        try:
            return await self._make_request(
                method="POST",
                endpoint="/api/models/incremental-learn",
                json_data={
                    "model_type": model_type,
                    "feedback_data": feedback_data
                }
            )
        except MLClientError as e:
            return {"error": str(e), "model_updated": False}
    
    async def evaluate_model(
        self,
        model_type: str,
        version_id: int
    ) -> Dict[str, Any]:
        """
        Evaluate a model version
        
        Args:
            model_type: Type of model
            version_id: Version ID to evaluate
            
        Returns:
            Evaluation metrics
        """
        try:
            return await self._make_request(
                method="POST",
                endpoint=f"/api/models/{version_id}/evaluate",
                params={"model_type": model_type}
            )
        except MLClientError as e:
            return {"error": str(e)}
    
    async def set_production_model(
        self,
        model_type: str,
        version_id: int
    ) -> Dict[str, Any]:
        """
        Set a model version as production
        
        Args:
            model_type: Type of model
            version_id: Version ID to promote
            
        Returns:
            Result of promotion
        """
        try:
            return await self._make_request(
                method="POST",
                endpoint=f"/api/models/{version_id}/set-production",
                params={"model_type": model_type}
            )
        except MLClientError as e:
            return {"error": str(e)}


# Global ML client instance
ml_client = MLClient()
