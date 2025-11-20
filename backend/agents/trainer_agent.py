"""
Model Trainer Agent - ML model training for vulnerability prediction
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime
import pickle
import os

from core.config import settings


class ModelTrainer:
    """AI agent for training vulnerability prediction models"""
    
    def __init__(self):
        self.model_path = "models/vulnerability_model.pkl"
        self.training_history = []
    
    async def train_model(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Train vulnerability prediction model"""
        
        if len(training_data) < 10:
            return {
                "success": False,
                "error": "Insufficient training data (minimum 10 samples required)"
            }
        
        X, y = self._prepare_training_data(training_data)
        
        model = self._build_model()
        
        history = self._train(model, X, y)
        
        self._save_model(model)
        
        return {
            "success": True,
            "samples": len(training_data),
            "accuracy": history["accuracy"],
            "loss": history["loss"],
            "trained_at": datetime.utcnow().isoformat()
        }
    
    def _prepare_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> tuple:
        """Prepare training data for model"""
        X = []
        y = []
        
        for sample in training_data:
            features = sample.get("features", [])
            label = sample.get("label", 0)
            
            if features:
                X.append(features)
                y.append(label)
        
        return np.array(X), np.array(y)
    
    def _build_model(self) -> Dict[str, Any]:
        """Build ML model"""
        model = {
            "type": "logistic_regression",
            "weights": None,
            "bias": None,
            "learning_rate": 0.01,
            "iterations": 1000
        }
        
        return model
    
    def _train(
        self,
        model: Dict[str, Any],
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, Any]:
        """Train model using gradient descent"""
        
        n_features = X.shape[1]
        weights = np.zeros(n_features)
        bias = 0
        
        learning_rate = model["learning_rate"]
        iterations = model["iterations"]
        
        m = len(y)
        
        for i in range(iterations):
            z = np.dot(X, weights) + bias
            predictions = 1 / (1 + np.exp(-z))
            
            dw = (1/m) * np.dot(X.T, (predictions - y))
            db = (1/m) * np.sum(predictions - y)
            
            weights -= learning_rate * dw
            bias -= learning_rate * db
        
        model["weights"] = weights
        model["bias"] = bias
        
        final_predictions = 1 / (1 + np.exp(-(np.dot(X, weights) + bias)))
        accuracy = np.mean((final_predictions > 0.5) == y)
        
        loss = -np.mean(y * np.log(final_predictions + 1e-15) + (1 - y) * np.log(1 - final_predictions + 1e-15))
        
        return {
            "accuracy": float(accuracy),
            "loss": float(loss)
        }
    
    def _save_model(self, model: Dict[str, Any]) -> None:
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        with open(self.model_path, "wb") as f:
            pickle.dump(model, f)
    
    def load_model(self) -> Dict[str, Any]:
        """Load trained model from disk"""
        if not os.path.exists(self.model_path):
            return None
        
        with open(self.model_path, "rb") as f:
            return pickle.load(f)
    
    async def evaluate_model(
        self,
        test_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate model performance"""
        
        model = self.load_model()
        
        if not model:
            return {
                "success": False,
                "error": "No trained model found"
            }
        
        X_test, y_test = self._prepare_training_data(test_data)
        
        weights = model["weights"]
        bias = model["bias"]
        
        z = np.dot(X_test, weights) + bias
        predictions = 1 / (1 + np.exp(-z))
        
        binary_predictions = (predictions > 0.5).astype(int)
        accuracy = np.mean(binary_predictions == y_test)
        
        true_positives = np.sum((binary_predictions == 1) & (y_test == 1))
        false_positives = np.sum((binary_predictions == 1) & (y_test == 0))
        true_negatives = np.sum((binary_predictions == 0) & (y_test == 0))
        false_negatives = np.sum((binary_predictions == 0) & (y_test == 1))
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "success": True,
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1_score),
            "confusion_matrix": {
                "true_positives": int(true_positives),
                "false_positives": int(false_positives),
                "true_negatives": int(true_negatives),
                "false_negatives": int(false_negatives)
            }
        }
    
    async def retrain_model(
        self,
        new_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Retrain model with new data"""
        
        existing_model = self.load_model()
        
        result = await self.train_model(new_data)
        
        if result["success"]:
            self.training_history.append({
                "trained_at": datetime.utcnow().isoformat(),
                "samples": len(new_data),
                "accuracy": result["accuracy"]
            })
        
        return result
