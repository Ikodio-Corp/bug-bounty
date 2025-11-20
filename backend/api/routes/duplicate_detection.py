"""
Duplicate Detection Routes
ML-based similarity detection, fuzzy matching
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from difflib import SequenceMatcher
import re

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.bug import Bug
from sqlalchemy import select

router = APIRouter(prefix="/duplicates", tags=["Duplicate Detection"])


class CheckDuplicateRequest(BaseModel):
    """Request to check for duplicates"""
    title: str
    description: str
    target_url: Optional[str] = None
    severity: Optional[str] = None


class MarkDuplicateRequest(BaseModel):
    """Request to mark bug as duplicate"""
    bug_id: int
    original_bug_id: int
    reason: Optional[str] = None


class SimilarityMatch(BaseModel):
    """Similarity match result"""
    bug_id: int
    title: str
    similarity_score: float
    match_type: str


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using SequenceMatcher
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        float: Similarity score (0-1)
    """
    text1_clean = text1.lower().strip()
    text2_clean = text2.lower().strip()
    return SequenceMatcher(None, text1_clean, text2_clean).ratio()


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        
    Returns:
        List[str]: Keywords
    """
    words = re.findall(r'\w+', text.lower())
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    return [w for w in words if w not in stopwords and len(w) > 3]


def calculate_keyword_similarity(keywords1: List[str], keywords2: List[str]) -> float:
    """
    Calculate keyword overlap similarity
    
    Args:
        keywords1: First keyword list
        keywords2: Second keyword list
        
    Returns:
        float: Similarity score (0-1)
    """
    if not keywords1 or not keywords2:
        return 0.0
    
    set1 = set(keywords1)
    set2 = set(keywords2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    return len(intersection) / len(union) if union else 0.0


def calculate_url_similarity(url1: str, url2: str) -> float:
    """
    Calculate URL similarity
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        float: Similarity score (0-1)
    """
    if not url1 or not url2:
        return 0.0
    
    url1_parts = url1.lower().split('/')
    url2_parts = url2.lower().split('/')
    
    common_parts = sum(1 for p1, p2 in zip(url1_parts, url2_parts) if p1 == p2)
    max_parts = max(len(url1_parts), len(url2_parts))
    
    return common_parts / max_parts if max_parts > 0 else 0.0


@router.post("/check")
async def check_duplicates(
    request: CheckDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check for duplicate bugs using ML-based similarity
    
    Args:
        request: Duplicate check request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Potential duplicates with similarity scores
    """
    try:
        # Get all existing bugs
        result = await db.execute(
            select(Bug).where(Bug.status != "duplicate")
        )
        existing_bugs = result.scalars().all()
        
        # Extract keywords from request
        request_keywords = extract_keywords(request.title + " " + request.description)
        
        potential_duplicates = []
        
        for bug in existing_bugs:
            # Calculate title similarity
            title_similarity = calculate_text_similarity(
                request.title,
                bug.title
            )
            
            # Calculate description similarity
            desc_similarity = calculate_text_similarity(
                request.description,
                bug.description or ""
            )
            
            # Calculate keyword similarity
            bug_keywords = extract_keywords(bug.title + " " + (bug.description or ""))
            keyword_similarity = calculate_keyword_similarity(
                request_keywords,
                bug_keywords
            )
            
            # Calculate URL similarity if provided
            url_similarity = 0.0
            if request.target_url and bug.target_url:
                url_similarity = calculate_url_similarity(
                    request.target_url,
                    bug.target_url
                )
            
            # Calculate weighted overall similarity
            overall_similarity = (
                title_similarity * 0.4 +
                desc_similarity * 0.3 +
                keyword_similarity * 0.2 +
                url_similarity * 0.1
            )
            
            # Determine match type
            match_type = "none"
            if title_similarity > 0.9:
                match_type = "exact_title"
            elif title_similarity > 0.7:
                match_type = "similar_title"
            elif overall_similarity > 0.6:
                match_type = "similar_content"
            
            # Add to potential duplicates if similarity is high enough
            if overall_similarity > 0.5:
                potential_duplicates.append({
                    "bug_id": bug.id,
                    "title": bug.title,
                    "severity": bug.severity,
                    "status": bug.status,
                    "similarity_score": round(overall_similarity, 2),
                    "title_similarity": round(title_similarity, 2),
                    "description_similarity": round(desc_similarity, 2),
                    "keyword_similarity": round(keyword_similarity, 2),
                    "url_similarity": round(url_similarity, 2),
                    "match_type": match_type,
                    "created_at": bug.created_at.isoformat()
                })
        
        # Sort by similarity score
        potential_duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Determine if likely duplicate
        is_likely_duplicate = len(potential_duplicates) > 0 and potential_duplicates[0]["similarity_score"] > 0.7
        
        return {
            "is_likely_duplicate": is_likely_duplicate,
            "total_matches": len(potential_duplicates),
            "potential_duplicates": potential_duplicates[:10],
            "recommendation": "Review similar bugs before submitting" if is_likely_duplicate else "No significant duplicates found"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Duplicate check failed: {str(e)}"
        )


@router.post("/mark")
async def mark_as_duplicate(
    request: MarkDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark bug as duplicate
    
    Args:
        request: Mark duplicate request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Update status
    """
    try:
        # Check admin permission
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can mark bugs as duplicates"
            )
        
        # Get the bug to be marked as duplicate
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Verify original bug exists
        original_result = await db.execute(
            select(Bug).where(Bug.id == request.original_bug_id)
        )
        original_bug = original_result.scalar_one_or_none()
        
        if not original_bug:
            raise HTTPException(status_code=404, detail="Original bug not found")
        
        # Mark as duplicate
        bug.status = "duplicate"
        bug.duplicate_of_id = request.original_bug_id
        bug.duplicate_marked_at = datetime.utcnow()
        bug.duplicate_reason = request.reason
        
        await db.commit()
        
        return {
            "status": "marked",
            "bug_id": request.bug_id,
            "original_bug_id": request.original_bug_id,
            "message": "Bug marked as duplicate"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark as duplicate: {str(e)}"
        )


@router.post("/unmark/{bug_id}")
async def unmark_duplicate(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unmark bug as duplicate
    
    Args:
        bug_id: Bug ID to unmark
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Update status
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can unmark duplicates"
            )
        
        result = await db.execute(
            select(Bug).where(Bug.id == bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.status != "duplicate":
            raise HTTPException(
                status_code=400,
                detail="Bug is not marked as duplicate"
            )
        
        # Unmark duplicate
        bug.status = "open"
        bug.duplicate_of_id = None
        bug.duplicate_marked_at = None
        bug.duplicate_reason = None
        
        await db.commit()
        
        return {
            "status": "unmarked",
            "bug_id": bug_id,
            "message": "Bug unmarked as duplicate"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unmark duplicate: {str(e)}"
        )


@router.get("/by-bug/{bug_id}")
async def find_duplicates_of_bug(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find duplicates of a specific bug
    
    Args:
        bug_id: Bug ID to check
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Potential duplicates
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Use check_duplicates logic
        request = CheckDuplicateRequest(
            title=bug.title,
            description=bug.description or "",
            target_url=bug.target_url,
            severity=bug.severity
        )
        
        return await check_duplicates(request, current_user, db)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find duplicates: {str(e)}"
        )


@router.get("/duplicates-of/{bug_id}")
async def get_bugs_marked_as_duplicates(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all bugs marked as duplicates of a specific bug
    
    Args:
        bug_id: Original bug ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Bugs marked as duplicates
    """
    try:
        result = await db.execute(
            select(Bug).where(
                Bug.duplicate_of_id == bug_id,
                Bug.status == "duplicate"
            )
        )
        duplicates = result.scalars().all()
        
        duplicate_list = []
        for dup in duplicates:
            hunter_result = await db.execute(
                select(User).where(User.id == dup.hunter_id)
            )
            hunter = hunter_result.scalar_one_or_none()
            
            duplicate_list.append({
                "bug_id": dup.id,
                "title": dup.title,
                "severity": dup.severity,
                "hunter": hunter.username if hunter else None,
                "marked_at": dup.duplicate_marked_at.isoformat() if dup.duplicate_marked_at else None,
                "reason": dup.duplicate_reason
            })
        
        return {
            "original_bug_id": bug_id,
            "total_duplicates": len(duplicate_list),
            "duplicates": duplicate_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get duplicates: {str(e)}"
        )


@router.get("/stats")
async def get_duplicate_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get duplicate detection statistics
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Duplicate statistics
    """
    try:
        # Get total duplicate count
        result = await db.execute(
            select(Bug).where(Bug.status == "duplicate")
        )
        total_duplicates = len(result.scalars().all())
        
        # Get unique original bugs
        result = await db.execute(
            select(Bug.duplicate_of_id).where(
                Bug.status == "duplicate",
                Bug.duplicate_of_id.isnot(None)
            ).distinct()
        )
        unique_originals = len(result.scalars().all())
        
        # Get total bugs
        total_result = await db.execute(select(Bug))
        total_bugs = len(total_result.scalars().all())
        
        duplicate_rate = (total_duplicates / total_bugs * 100) if total_bugs > 0 else 0
        
        return {
            "total_bugs": total_bugs,
            "total_duplicates": total_duplicates,
            "unique_original_bugs": unique_originals,
            "duplicate_rate": round(duplicate_rate, 2),
            "average_duplicates_per_bug": round(total_duplicates / unique_originals, 2) if unique_originals > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.post("/batch-check")
async def batch_check_duplicates(
    bug_ids: List[int] = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Batch check multiple bugs for duplicates
    
    Args:
        bug_ids: List of bug IDs to check
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Batch check results
    """
    try:
        results = []
        
        for bug_id in bug_ids:
            result = await db.execute(
                select(Bug).where(Bug.id == bug_id)
            )
            bug = result.scalar_one_or_none()
            
            if not bug:
                results.append({
                    "bug_id": bug_id,
                    "error": "Bug not found"
                })
                continue
            
            # Check for duplicates
            request = CheckDuplicateRequest(
                title=bug.title,
                description=bug.description or "",
                target_url=bug.target_url,
                severity=bug.severity
            )
            
            duplicate_check = await check_duplicates(request, current_user, db)
            
            results.append({
                "bug_id": bug_id,
                "is_likely_duplicate": duplicate_check["is_likely_duplicate"],
                "total_matches": duplicate_check["total_matches"],
                "top_match": duplicate_check["potential_duplicates"][0] if duplicate_check["potential_duplicates"] else None
            })
        
        return {
            "total_checked": len(bug_ids),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch check failed: {str(e)}"
        )
