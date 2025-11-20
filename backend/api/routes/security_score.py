"""
Security Score API Routes
FICO-style security credit score endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from services.security_score_service import SecurityScoreService
from models.user import User


router = APIRouter(prefix="/api/security-score", tags=["Security Score"])


@router.get("/calculate")
async def calculate_score(
    company_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate security credit score for company
    """
    
    target_company_id = company_id if company_id else current_user.id
    
    service = SecurityScoreService(db)
    
    try:
        score_data = await service.calculate_score(target_company_id)
        
        return {
            "success": True,
            "data": score_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/save")
async def save_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate and save security score to database
    """
    
    service = SecurityScoreService(db)
    
    try:
        score = await service.save_score(current_user.id)
        
        return {
            "success": True,
            "data": {
                "score_id": score.id,
                "score": score.score,
                "grade": score.grade,
                "calculated_at": score.calculated_at,
                "valid_until": score.valid_until
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{company_id}")
async def get_score(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get latest security score for company
    """
    
    from models.security_score import SecurityScore
    
    score = db.query(SecurityScore).filter(
        SecurityScore.company_id == company_id
    ).order_by(SecurityScore.calculated_at.desc()).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return {
        "success": True,
        "data": {
            "score": score.score,
            "grade": score.grade,
            "components": {
                "technical_security": score.technical_security_score,
                "process_maturity": score.process_maturity_score,
                "compliance": score.compliance_score,
                "historical_track_record": score.historical_track_record_score
            },
            "vulnerabilities": {
                "total": score.vulnerability_count,
                "critical": score.critical_vulnerabilities,
                "high": score.high_vulnerabilities
            },
            "calculated_at": score.calculated_at,
            "valid_until": score.valid_until
        }
    }


@router.post("/report")
async def generate_report(
    report_type: str = "standard",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate detailed security score report
    """
    
    service = SecurityScoreService(db)
    
    try:
        report = await service.generate_report(
            company_id=current_user.id,
            report_type=report_type
        )
        
        return {
            "success": True,
            "data": {
                "report_id": report.id,
                "report_type": report.report_type,
                "executive_summary": report.executive_summary,
                "recommendations": report.recommendations,
                "generated_at": report.generated_at
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{company_id}")
async def get_score_history(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get security score history for trend analysis
    """
    
    from models.security_score import SecurityScoreHistory
    
    history = db.query(SecurityScoreHistory).filter(
        SecurityScoreHistory.company_id == company_id
    ).order_by(SecurityScoreHistory.recorded_at.desc()).limit(12).all()
    
    return {
        "success": True,
        "data": [
            {
                "score": entry.score,
                "change_from_previous": entry.change_from_previous,
                "recorded_at": entry.recorded_at
            }
            for entry in history
        ]
    }
