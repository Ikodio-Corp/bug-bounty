"""
Vulnerability Predictor Agent - ML-based vulnerability prediction
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime

from core.config import settings


class VulnerabilityPredictor:
    """AI agent for predicting vulnerabilities"""
    
    def __init__(self):
        self.model = None
        self.features = []
    
    async def predict_vulnerabilities(
        self,
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict potential vulnerabilities based on target characteristics"""
        
        features = self._extract_features(target_data)
        
        predictions = {
            "target": target_data.get("url", "unknown"),
            "predicted_at": datetime.utcnow().isoformat(),
            "predictions": []
        }
        
        vulnerability_types = ["xss", "sqli", "rce", "csrf", "ssrf"]
        
        for vuln_type in vulnerability_types:
            probability = self._calculate_probability(features, vuln_type)
            
            if probability > 0.3:
                predictions["predictions"].append({
                    "type": vuln_type,
                    "probability": probability,
                    "confidence": self._calculate_confidence(features),
                    "risk_score": probability * 10
                })
        
        predictions["predictions"].sort(key=lambda x: x["probability"], reverse=True)
        
        return predictions
    
    def _extract_features(self, target_data: Dict[str, Any]) -> List[float]:
        """Extract features from target data"""
        features = []
        
        url = target_data.get("url", "")
        features.append(1.0 if "?" in url else 0.0)
        features.append(1.0 if "id=" in url else 0.0)
        features.append(1.0 if "search=" in url else 0.0)
        
        tech_stack = target_data.get("technology", [])
        features.append(1.0 if "php" in tech_stack else 0.0)
        features.append(1.0 if "mysql" in tech_stack else 0.0)
        features.append(1.0 if "javascript" in tech_stack else 0.0)
        
        features.append(target_data.get("complexity", 0.5))
        features.append(target_data.get("age_years", 5) / 10)
        
        return features
    
    def _calculate_probability(self, features: List[float], vuln_type: str) -> float:
        """Calculate vulnerability probability"""
        
        weights = {
            "xss": [0.3, 0.1, 0.4, 0.2, 0.0, 0.5, 0.3, 0.2],
            "sqli": [0.2, 0.5, 0.1, 0.4, 0.4, 0.2, 0.3, 0.3],
            "rce": [0.1, 0.2, 0.1, 0.5, 0.3, 0.4, 0.4, 0.4],
            "csrf": [0.2, 0.2, 0.2, 0.3, 0.1, 0.4, 0.3, 0.2],
            "ssrf": [0.1, 0.3, 0.3, 0.2, 0.2, 0.3, 0.4, 0.3]
        }
        
        if vuln_type not in weights:
            return 0.5
        
        w = weights[vuln_type]
        
        if len(features) != len(w):
            return 0.5
        
        score = sum(f * weight for f, weight in zip(features, w))
        probability = 1 / (1 + np.exp(-score))
        
        return float(probability)
    
    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate prediction confidence"""
        feature_quality = sum(1 for f in features if f > 0) / len(features)
        return min(feature_quality + 0.3, 1.0)
    
    async def analyze_patterns(
        self,
        historical_vulns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns in historical vulnerabilities"""
        
        if not historical_vulns:
            return {"patterns": [], "insights": "Insufficient data"}
        
        patterns = {
            "common_types": {},
            "severity_distribution": {},
            "trends": []
        }
        
        for vuln in historical_vulns:
            vuln_type = vuln.get("type", "unknown")
            severity = vuln.get("severity", "unknown")
            
            patterns["common_types"][vuln_type] = patterns["common_types"].get(vuln_type, 0) + 1
            patterns["severity_distribution"][severity] = patterns["severity_distribution"].get(severity, 0) + 1
        
        sorted_types = sorted(
            patterns["common_types"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        patterns["top_types"] = [{"type": t, "count": c} for t, c in sorted_types[:5]]
        
        total = len(historical_vulns)
        patterns["insights"] = f"Analyzed {total} vulnerabilities. Most common: {sorted_types[0][0] if sorted_types else 'N/A'}"
        
        return patterns
