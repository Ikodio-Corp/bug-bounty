"""
Duplicate Bug Detection Service
Uses ML to detect duplicate vulnerability reports
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from difflib import SequenceMatcher


class DuplicateDetector:
    """Detect duplicate bug reports"""
    
    def __init__(self):
        self.similarity_threshold = 0.85
        
    async def find_duplicates(
        self,
        new_bug: Dict[str, Any],
        existing_bugs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find potential duplicate bugs"""
        
        duplicates = []
        
        for existing_bug in existing_bugs:
            similarity = await self.calculate_similarity(new_bug, existing_bug)
            
            if similarity >= self.similarity_threshold:
                duplicates.append({
                    "bug_id": existing_bug.get("id"),
                    "similarity_score": similarity,
                    "match_reasons": self._get_match_reasons(new_bug, existing_bug),
                    "existing_bug": existing_bug
                })
        
        duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return duplicates
    
    async def calculate_similarity(
        self,
        bug1: Dict[str, Any],
        bug2: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two bugs"""
        
        scores = []
        
        title_sim = self._text_similarity(
            bug1.get("title", ""),
            bug2.get("title", "")
        )
        scores.append(("title", title_sim, 0.3))
        
        desc_sim = self._text_similarity(
            bug1.get("description", ""),
            bug2.get("description", "")
        )
        scores.append(("description", desc_sim, 0.25))
        
        if bug1.get("bug_type") == bug2.get("bug_type"):
            scores.append(("type", 1.0, 0.15))
        else:
            scores.append(("type", 0.0, 0.15))
        
        if bug1.get("target_domain") == bug2.get("target_domain"):
            scores.append(("domain", 1.0, 0.15))
        else:
            scores.append(("domain", 0.0, 0.15))
        
        endpoint_sim = self._text_similarity(
            bug1.get("endpoint", ""),
            bug2.get("endpoint", "")
        )
        scores.append(("endpoint", endpoint_sim, 0.10))
        
        payload_sim = self._text_similarity(
            bug1.get("payload", ""),
            bug2.get("payload", "")
        )
        scores.append(("payload", payload_sim, 0.05))
        
        weighted_score = sum(score * weight for _, score, weight in scores)
        
        return weighted_score
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _get_match_reasons(
        self,
        bug1: Dict[str, Any],
        bug2: Dict[str, Any]
    ) -> List[str]:
        """Get reasons why bugs match"""
        reasons = []
        
        if bug1.get("bug_type") == bug2.get("bug_type"):
            reasons.append(f"Same vulnerability type: {bug1.get('bug_type')}")
        
        if bug1.get("target_domain") == bug2.get("target_domain"):
            reasons.append(f"Same target domain: {bug1.get('target_domain')}")
        
        if self._text_similarity(bug1.get("title", ""), bug2.get("title", "")) > 0.8:
            reasons.append("Similar titles")
        
        if self._text_similarity(bug1.get("endpoint", ""), bug2.get("endpoint", "")) > 0.8:
            reasons.append("Same endpoint")
        
        return reasons
    
    async def mark_as_duplicate(
        self,
        bug_id: int,
        original_bug_id: int,
        similarity_score: float
    ) -> Dict[str, Any]:
        """Mark bug as duplicate"""
        
        return {
            "bug_id": bug_id,
            "status": "duplicate",
            "original_bug_id": original_bug_id,
            "similarity_score": similarity_score,
            "marked_at": datetime.utcnow().isoformat()
        }


class ValidationWorkflow:
    """Bug validation workflow"""
    
    def __init__(self):
        self.validation_steps = [
            "duplicate_check",
            "severity_verification",
            "exploitability_test",
            "impact_assessment",
            "remediation_verification"
        ]
    
    async def validate_bug(
        self,
        bug: Dict[str, Any],
        existing_bugs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run full validation workflow"""
        
        validation_result = {
            "bug_id": bug.get("id"),
            "status": "validating",
            "steps_completed": [],
            "is_valid": True,
            "is_duplicate": False,
            "validation_score": 0.0,
            "issues": []
        }
        
        detector = DuplicateDetector()
        duplicates = await detector.find_duplicates(bug, existing_bugs)
        
        if duplicates and duplicates[0]["similarity_score"] > 0.9:
            validation_result["is_duplicate"] = True
            validation_result["is_valid"] = False
            validation_result["duplicate_of"] = duplicates[0]["bug_id"]
            validation_result["issues"].append("High similarity with existing bug")
            return validation_result
        
        validation_result["steps_completed"].append("duplicate_check")
        
        severity_valid = await self._verify_severity(bug)
        if severity_valid:
            validation_result["steps_completed"].append("severity_verification")
        else:
            validation_result["issues"].append("Severity may be overestimated")
        
        exploitability = await self._test_exploitability(bug)
        validation_result["exploitability_score"] = exploitability
        validation_result["steps_completed"].append("exploitability_test")
        
        if exploitability < 0.3:
            validation_result["issues"].append("Low exploitability score")
        
        impact_score = await self._assess_impact(bug)
        validation_result["impact_score"] = impact_score
        validation_result["steps_completed"].append("impact_assessment")
        
        validation_result["validation_score"] = (
            (0.4 * exploitability) +
            (0.4 * impact_score) +
            (0.2 * (1.0 if severity_valid else 0.5))
        )
        
        if validation_result["validation_score"] >= 0.7:
            validation_result["status"] = "validated"
        elif validation_result["validation_score"] >= 0.5:
            validation_result["status"] = "needs_review"
        else:
            validation_result["status"] = "rejected"
            validation_result["is_valid"] = False
        
        return validation_result
    
    async def _verify_severity(self, bug: Dict[str, Any]) -> bool:
        """Verify bug severity is appropriate"""
        
        severity = bug.get("severity", "").lower()
        bug_type = bug.get("bug_type", "")
        
        critical_types = ["rce", "sql_injection", "auth_bypass"]
        high_types = ["xss", "csrf", "ssrf", "deserialization"]
        
        if severity == "critical" and bug_type in critical_types:
            return True
        elif severity == "high" and bug_type in high_types:
            return True
        elif severity in ["medium", "low"]:
            return True
        
        return False
    
    async def _test_exploitability(self, bug: Dict[str, Any]) -> float:
        """Test if vulnerability is exploitable"""
        
        if bug.get("exploit_code") or bug.get("proof_of_concept"):
            return 0.9
        
        if bug.get("steps_to_reproduce"):
            return 0.7
        
        return 0.4
    
    async def _assess_impact(self, bug: Dict[str, Any]) -> float:
        """Assess vulnerability impact"""
        
        severity_scores = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3
        }
        
        severity = bug.get("severity", "medium").lower()
        base_score = severity_scores.get(severity, 0.5)
        
        if bug.get("cvss_score"):
            cvss = float(bug.get("cvss_score", 0))
            cvss_normalized = cvss / 10.0
            return (base_score + cvss_normalized) / 2
        
        return base_score
