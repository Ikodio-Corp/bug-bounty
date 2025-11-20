"""
Auto-Reporting to Bug Bounty Platforms
HackerOne, Bugcrowd, Intigriti, YesWeHack
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.bug import Bug
from sqlalchemy import select

router = APIRouter(prefix="/auto-reporting", tags=["Auto Reporting"])


class PlatformConfig(BaseModel):
    """Bug bounty platform configuration"""
    platform: str
    api_token: str
    username: Optional[str] = None


class SubmitReportRequest(BaseModel):
    """Request to submit bug report to platform"""
    bug_id: int
    platform: str
    program_id: str
    severity: Optional[str] = None
    asset_identifier: Optional[str] = None


class HackerOneClient:
    """HackerOne API client"""
    
    def __init__(self, username: str, api_token: str):
        self.username = username
        self.api_token = api_token
        self.base_url = "https://api.hackerone.com/v1"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def create_report(
        self,
        program_handle: str,
        title: str,
        vulnerability_information: str,
        impact: str,
        severity_rating: str = "medium",
        weakness_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create report on HackerOne"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/reports",
                headers=self.headers,
                auth=(self.username, self.api_token),
                json={
                    "data": {
                        "type": "report",
                        "attributes": {
                            "team_handle": program_handle,
                            "title": title,
                            "vulnerability_information": vulnerability_information,
                            "impact": impact,
                            "severity_rating": severity_rating,
                            "weakness_id": weakness_id
                        }
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """Get report details"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reports/{report_id}",
                headers=self.headers,
                auth=(self.username, self.api_token)
            )
            response.raise_for_status()
            return response.json()


class BugcrowdClient:
    """Bugcrowd API client"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.bugcrowd.com"
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Accept": "application/vnd.bugcrowd.v4+json",
            "Content-Type": "application/json"
        }
    
    async def create_submission(
        self,
        program_code: str,
        title: str,
        description: str,
        severity: int = 3,
        target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create submission on Bugcrowd"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/submissions",
                headers=self.headers,
                json={
                    "program_code": program_code,
                    "title": title,
                    "description": description,
                    "severity": severity,
                    "target": target,
                    "vrt": {
                        "category": "broken_access_control",
                        "subcategory": "authorization_bypass"
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_submission(self, submission_uuid: str) -> Dict[str, Any]:
        """Get submission details"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/submissions/{submission_uuid}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


class IntigritiClient:
    """Intigriti API client"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.intigriti.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def create_submission(
        self,
        program_id: str,
        title: str,
        description: str,
        severity: str = "medium",
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create submission on Intigriti"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/core/researcher/submissions",
                headers=self.headers,
                json={
                    "programId": program_id,
                    "title": title,
                    "description": description,
                    "severity": severity,
                    "endpoint": endpoint
                }
            )
            response.raise_for_status()
            return response.json()


class YesWeHackClient:
    """YesWeHack API client"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.yeswehack.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def create_report(
        self,
        program_slug: str,
        title: str,
        description: str,
        cvss: float = 5.0,
        scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create report on YesWeHack"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/programs/{program_slug}/reports",
                headers=self.headers,
                json={
                    "title": title,
                    "description": description,
                    "cvss": cvss,
                    "scope": scope
                }
            )
            response.raise_for_status()
            return response.json()


@router.post("/hackerone/configure")
async def configure_hackerone(
    config: PlatformConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure HackerOne integration
    
    Args:
        config: HackerOne configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Store configuration
        current_user.hackerone_username = config.username
        current_user.hackerone_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "hackerone",
            "username": config.username,
            "message": "HackerOne integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"HackerOne configuration failed: {str(e)}"
        )


@router.post("/hackerone/submit")
async def submit_to_hackerone(
    request: SubmitReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit bug report to HackerOne
    
    Args:
        request: Submit request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Submission status with HackerOne report ID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.hunter_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only submit your own bugs"
            )
        
        # Check HackerOne configuration
        if not current_user.hackerone_username or not current_user.hackerone_token:
            raise HTTPException(
                status_code=400,
                detail="HackerOne not configured"
            )
        
        # Create HackerOne client
        client = HackerOneClient(
            username=current_user.hackerone_username,
            api_token=current_user.hackerone_token
        )
        
        # Map severity
        severity_map = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
        severity = severity_map.get(bug.severity, "medium")
        
        # Create report
        report = await client.create_report(
            program_handle=request.program_id,
            title=bug.title,
            vulnerability_information=bug.description or "",
            impact=bug.impact or "",
            severity_rating=severity
        )
        
        # Store HackerOne report reference
        bug.platform_name = "hackerone"
        bug.platform_program_id = request.program_id
        bug.platform_report_id = report["data"]["id"]
        bug.reported_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "submitted",
            "bug_id": request.bug_id,
            "platform": "hackerone",
            "report_id": report["data"]["id"],
            "message": "Report submitted to HackerOne successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"HackerOne submission failed: {str(e)}"
        )


@router.post("/bugcrowd/configure")
async def configure_bugcrowd(
    config: PlatformConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Bugcrowd integration
    
    Args:
        config: Bugcrowd configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Store configuration
        current_user.bugcrowd_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "bugcrowd",
            "message": "Bugcrowd integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Bugcrowd configuration failed: {str(e)}"
        )


@router.post("/bugcrowd/submit")
async def submit_to_bugcrowd(
    request: SubmitReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit bug report to Bugcrowd
    
    Args:
        request: Submit request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Submission status with Bugcrowd submission UUID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.hunter_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only submit your own bugs"
            )
        
        # Check Bugcrowd configuration
        if not current_user.bugcrowd_token:
            raise HTTPException(
                status_code=400,
                detail="Bugcrowd not configured"
            )
        
        # Create Bugcrowd client
        client = BugcrowdClient(api_token=current_user.bugcrowd_token)
        
        # Map severity to Bugcrowd scale (1-5)
        severity_map = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "info": 1
        }
        severity = severity_map.get(bug.severity, 3)
        
        # Create submission
        submission = await client.create_submission(
            program_code=request.program_id,
            title=bug.title,
            description=bug.description or "",
            severity=severity,
            target=request.asset_identifier
        )
        
        # Store Bugcrowd submission reference
        bug.platform_name = "bugcrowd"
        bug.platform_program_id = request.program_id
        bug.platform_report_id = submission["uuid"]
        bug.reported_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "submitted",
            "bug_id": request.bug_id,
            "platform": "bugcrowd",
            "submission_uuid": submission["uuid"],
            "message": "Submission created on Bugcrowd successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Bugcrowd submission failed: {str(e)}"
        )


@router.post("/intigriti/configure")
async def configure_intigriti(
    config: PlatformConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Intigriti integration
    
    Args:
        config: Intigriti configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Store configuration
        current_user.intigriti_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "intigriti",
            "message": "Intigriti integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Intigriti configuration failed: {str(e)}"
        )


@router.post("/intigriti/submit")
async def submit_to_intigriti(
    request: SubmitReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit bug report to Intigriti
    
    Args:
        request: Submit request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Submission status with Intigriti submission ID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.hunter_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only submit your own bugs"
            )
        
        # Check Intigriti configuration
        if not current_user.intigriti_token:
            raise HTTPException(
                status_code=400,
                detail="Intigriti not configured"
            )
        
        # Create Intigriti client
        client = IntigritiClient(api_token=current_user.intigriti_token)
        
        # Create submission
        submission = await client.create_submission(
            program_id=request.program_id,
            title=bug.title,
            description=bug.description or "",
            severity=bug.severity,
            endpoint=bug.target_url
        )
        
        # Store Intigriti submission reference
        bug.platform_name = "intigriti"
        bug.platform_program_id = request.program_id
        bug.platform_report_id = submission["submissionId"]
        bug.reported_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "submitted",
            "bug_id": request.bug_id,
            "platform": "intigriti",
            "submission_id": submission["submissionId"],
            "message": "Submission created on Intigriti successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Intigriti submission failed: {str(e)}"
        )


@router.post("/yeswehack/configure")
async def configure_yeswehack(
    config: PlatformConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure YesWeHack integration
    
    Args:
        config: YesWeHack configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Store configuration
        current_user.yeswehack_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "yeswehack",
            "message": "YesWeHack integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"YesWeHack configuration failed: {str(e)}"
        )


@router.post("/yeswehack/submit")
async def submit_to_yeswehack(
    request: SubmitReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit bug report to YesWeHack
    
    Args:
        request: Submit request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Submission status with YesWeHack report ID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.hunter_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only submit your own bugs"
            )
        
        # Check YesWeHack configuration
        if not current_user.yeswehack_token:
            raise HTTPException(
                status_code=400,
                detail="YesWeHack not configured"
            )
        
        # Create YesWeHack client
        client = YesWeHackClient(api_token=current_user.yeswehack_token)
        
        # Create report
        report = await client.create_report(
            program_slug=request.program_id,
            title=bug.title,
            description=bug.description or "",
            cvss=bug.cvss_score or 5.0,
            scope=bug.target_url
        )
        
        # Store YesWeHack report reference
        bug.platform_name = "yeswehack"
        bug.platform_program_id = request.program_id
        bug.platform_report_id = report["report_id"]
        bug.reported_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "submitted",
            "bug_id": request.bug_id,
            "platform": "yeswehack",
            "report_id": report["report_id"],
            "message": "Report submitted to YesWeHack successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"YesWeHack submission failed: {str(e)}"
        )


@router.get("/status/{bug_id}")
async def get_submission_status(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get submission status for bug
    
    Args:
        bug_id: Bug ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Submission status across all platforms
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        return {
            "bug_id": bug_id,
            "submitted": bug.platform_name is not None,
            "platform": bug.platform_name,
            "program_id": bug.platform_program_id,
            "report_id": bug.platform_report_id,
            "reported_at": bug.reported_at.isoformat() if bug.reported_at else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get submission status: {str(e)}"
        )


@router.get("/platforms")
async def get_configured_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get configured platforms for user
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configured platforms
    """
    try:
        platforms = {
            "hackerone": {
                "configured": current_user.hackerone_username is not None and current_user.hackerone_token is not None,
                "username": current_user.hackerone_username
            },
            "bugcrowd": {
                "configured": current_user.bugcrowd_token is not None
            },
            "intigriti": {
                "configured": current_user.intigriti_token is not None
            },
            "yeswehack": {
                "configured": current_user.yeswehack_token is not None
            }
        }
        
        return {
            "platforms": platforms,
            "total_configured": sum(1 for p in platforms.values() if p["configured"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get platforms: {str(e)}"
        )
