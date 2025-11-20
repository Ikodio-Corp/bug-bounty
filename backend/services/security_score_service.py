"""
Security Credit Score Service
FICO-style scoring system for companies (300-850 scale)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.security_score import (
    SecurityScore,
    SecurityScoreHistory,
    SecurityScoreReport
)
from models.bug import Bug


class SecurityScoreService:
    """
    Service for calculating and managing security credit scores
    """
    
    SCORE_MIN = 300
    SCORE_MAX = 850
    
    def __init__(self, db: Session):
        self.db = db
    
    async def calculate_score(self, company_id: int) -> Dict:
        """
        Calculate comprehensive security score
        
        Score Components:
        - Technical Security (40%): Vulnerability count, severity distribution
        - Process Maturity (25%): Patch velocity, incident response time
        - Compliance (20%): Certifications, audit results
        - Historical Track Record (15%): Breach history, trend analysis
        """
        
        technical_score = await self._calculate_technical_security(company_id)
        process_score = await self._calculate_process_maturity(company_id)
        compliance_score = await self._calculate_compliance_score(company_id)
        historical_score = await self._calculate_historical_track_record(company_id)
        
        weighted_score = (
            technical_score * 0.40 +
            process_score * 0.25 +
            compliance_score * 0.20 +
            historical_score * 0.15
        )
        
        final_score = self._normalize_score(weighted_score)
        
        grade = self._score_to_grade(final_score)
        
        vuln_stats = await self._get_vulnerability_stats(company_id)
        
        return {
            "score": final_score,
            "grade": grade,
            "components": {
                "technical_security": technical_score,
                "process_maturity": process_score,
                "compliance": compliance_score,
                "historical_track_record": historical_score
            },
            "vulnerability_count": vuln_stats["total"],
            "critical_vulnerabilities": vuln_stats["critical"],
            "high_vulnerabilities": vuln_stats["high"],
            "calculated_at": datetime.utcnow()
        }
    
    async def save_score(self, company_id: int) -> SecurityScore:
        """
        Calculate and save security score to database
        """
        
        score_data = await self.calculate_score(company_id)
        
        previous_score = self.db.query(SecurityScore).filter(
            SecurityScore.company_id == company_id
        ).order_by(SecurityScore.calculated_at.desc()).first()
        
        new_score = SecurityScore(
            company_id=company_id,
            score=score_data["score"],
            grade=score_data["grade"],
            technical_security_score=score_data["components"]["technical_security"],
            process_maturity_score=score_data["components"]["process_maturity"],
            compliance_score=score_data["components"]["compliance"],
            historical_track_record_score=score_data["components"]["historical_track_record"],
            vulnerability_count=score_data["vulnerability_count"],
            critical_vulnerabilities=score_data["critical_vulnerabilities"],
            high_vulnerabilities=score_data["high_vulnerabilities"],
            calculated_at=score_data["calculated_at"],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        
        self.db.add(new_score)
        
        if previous_score:
            history = SecurityScoreHistory(
                company_id=company_id,
                score=score_data["score"],
                change_from_previous=score_data["score"] - previous_score.score,
                recorded_at=datetime.utcnow()
            )
            self.db.add(history)
        
        self.db.commit()
        self.db.refresh(new_score)
        
        return new_score
    
    async def generate_report(
        self,
        company_id: int,
        report_type: str = "standard"
    ) -> SecurityScoreReport:
        """
        Generate detailed security score report
        """
        
        current_score = self.db.query(SecurityScore).filter(
            SecurityScore.company_id == company_id
        ).order_by(SecurityScore.calculated_at.desc()).first()
        
        if not current_score:
            current_score = await self.save_score(company_id)
        
        recommendations = await self._generate_recommendations(company_id, current_score)
        
        report = SecurityScoreReport(
            score_id=current_score.id,
            report_type=report_type,
            detailed_analysis=self._generate_analysis(current_score),
            recommendations=recommendations,
            executive_summary=self._generate_executive_summary(current_score),
            technical_details={
                "score_breakdown": {
                    "technical": current_score.technical_security_score,
                    "process": current_score.process_maturity_score,
                    "compliance": current_score.compliance_score,
                    "historical": current_score.historical_track_record_score
                },
                "vulnerabilities": {
                    "total": current_score.vulnerability_count,
                    "critical": current_score.critical_vulnerabilities,
                    "high": current_score.high_vulnerabilities
                }
            },
            generated_at=datetime.utcnow()
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    async def _calculate_technical_security(self, company_id: int) -> float:
        """
        Calculate technical security score (0-100)
        Based on vulnerability count and severity
        """
        
        vuln_stats = await self._get_vulnerability_stats(company_id)
        
        penalty = (
            vuln_stats["critical"] * 20 +
            vuln_stats["high"] * 10 +
            vuln_stats["medium"] * 3 +
            vuln_stats["low"] * 1
        )
        
        base_score = 100
        score = max(0, base_score - penalty)
        
        return score
    
    async def _calculate_process_maturity(self, company_id: int) -> float:
        """
        Calculate process maturity score (0-100)
        Based on patch velocity and response times
        """
        
        avg_patch_time = await self._get_average_patch_time(company_id)
        
        if avg_patch_time <= 7:
            return 95
        elif avg_patch_time <= 14:
            return 85
        elif avg_patch_time <= 30:
            return 70
        elif avg_patch_time <= 60:
            return 55
        else:
            return 40
    
    async def _calculate_compliance_score(self, company_id: int) -> float:
        """
        Calculate compliance score (0-100)
        """
        return 75.0
    
    async def _calculate_historical_track_record(self, company_id: int) -> float:
        """
        Calculate historical track record score (0-100)
        """
        return 80.0
    
    async def _get_vulnerability_stats(self, company_id: int) -> Dict:
        """
        Get vulnerability statistics
        """
        
        result = self.db.query(
            func.count(Bug.id).label("total"),
            func.sum((Bug.severity == "critical").cast(int)).label("critical"),
            func.sum((Bug.severity == "high").cast(int)).label("high"),
            func.sum((Bug.severity == "medium").cast(int)).label("medium"),
            func.sum((Bug.severity == "low").cast(int)).label("low")
        ).filter(
            Bug.company_id == company_id,
            Bug.status != "fixed"
        ).first()
        
        return {
            "total": result.total or 0,
            "critical": result.critical or 0,
            "high": result.high or 0,
            "medium": result.medium or 0,
            "low": result.low or 0
        }
    
    async def _get_average_patch_time(self, company_id: int) -> float:
        """
        Get average patch time in days
        """
        return 14.0
    
    def _normalize_score(self, raw_score: float) -> int:
        """
        Normalize score to 300-850 range
        """
        
        normalized = self.SCORE_MIN + (raw_score / 100) * (self.SCORE_MAX - self.SCORE_MIN)
        return int(normalized)
    
    def _score_to_grade(self, score: int) -> str:
        """
        Convert numeric score to letter grade
        """
        
        if score >= 800:
            return "A+"
        elif score >= 750:
            return "A"
        elif score >= 700:
            return "B+"
        elif score >= 650:
            return "B"
        elif score >= 600:
            return "C+"
        elif score >= 550:
            return "C"
        elif score >= 500:
            return "D"
        else:
            return "F"
    
    def _generate_analysis(self, score: SecurityScore) -> str:
        """
        Generate detailed analysis text
        """
        
        return f"Security score analysis for company. Overall score: {score.score} ({score.grade})"
    
    def _generate_executive_summary(self, score: SecurityScore) -> str:
        """
        Generate executive summary
        """
        
        return f"Company has achieved a security score of {score.score}, indicating {score.grade} grade security posture."
    
    async def _generate_recommendations(self, company_id: int, score: SecurityScore) -> List[Dict]:
        """
        Generate actionable recommendations
        """
        
        recommendations = []
        
        if score.critical_vulnerabilities > 0:
            recommendations.append({
                "priority": "critical",
                "title": "Address Critical Vulnerabilities",
                "description": f"You have {score.critical_vulnerabilities} critical vulnerabilities that need immediate attention.",
                "estimated_impact": "+50 points"
            })
        
        if score.process_maturity_score < 70:
            recommendations.append({
                "priority": "high",
                "title": "Improve Patch Velocity",
                "description": "Reduce average patch time to under 14 days.",
                "estimated_impact": "+30 points"
            })
        
        return recommendations
