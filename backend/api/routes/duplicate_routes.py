"""
Duplicate Detection API Routes - Bug Similarity Detection Endpoints

This module provides REST API endpoints for duplicate bug detection
including similarity analysis and cluster identification.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...services.duplicate_detection import (
    get_duplicate_service,
    DuplicateDetectionService
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/duplicates", tags=["Duplicate Detection"])


# Request Models
class AddBugRequest(BaseModel):
    """Request to add bug to detection index."""
    bug_id: str = Field(..., description="Bug ID")
    title: str = Field(..., description="Bug title")
    description: str = Field(..., description="Bug description")
    proof_of_concept: str = Field(default="", description="POC code")
    reproduction_steps: str = Field(default="", description="Steps to reproduce")
    vulnerability_type: str = Field(default="", description="Vulnerability type")
    affected_component: str = Field(default="", description="Affected component")
    program_id: str = Field(default="", description="Program ID")


class BatchAddRequest(BaseModel):
    """Request to add multiple bugs."""
    bugs: List[AddBugRequest] = Field(..., description="List of bugs to add")


class ThresholdUpdateRequest(BaseModel):
    """Request to update detection thresholds."""
    title: Optional[float] = Field(None, description="Title similarity threshold")
    description: Optional[float] = Field(None, description="Description similarity threshold")
    code: Optional[float] = Field(None, description="Code similarity threshold")
    url: Optional[float] = Field(None, description="URL similarity threshold")
    overall: Optional[float] = Field(None, description="Overall threshold")


# Dependency
async def get_service() -> DuplicateDetectionService:
    """Get duplicate detection service."""
    return get_duplicate_service()


# Index Management Endpoints
@router.post("/index", response_model=Dict[str, Any])
async def add_bug_to_index(
    request: AddBugRequest,
    service: DuplicateDetectionService = Depends(get_service)
):
    """
    Add bug to detection index.

    Preprocesses and stores bug data for similarity matching.
    """
    try:
        service.add_bug(request.bug_id, request.dict())

        return {
            "success": True,
            "bug_id": request.bug_id,
            "message": "Bug added to index"
        }

    except Exception as e:
        logger.error(f"Add bug to index failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/batch", response_model=Dict[str, Any])
async def batch_add_bugs(
    request: BatchAddRequest,
    service: DuplicateDetectionService = Depends(get_service)
):
    """Add multiple bugs to detection index."""
    try:
        added = 0
        for bug in request.bugs:
            service.add_bug(bug.bug_id, bug.dict())
            added += 1

        return {
            "success": True,
            "bugs_added": added,
            "message": f"{added} bugs added to index"
        }

    except Exception as e:
        logger.error(f"Batch add bugs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Detection Endpoints
@router.get("/detect/{bug_id}", response_model=Dict[str, Any])
async def detect_duplicates(
    bug_id: str,
    program_id: Optional[str] = Query(None, description="Filter by program"),
    limit: int = Query(10, description="Max results"),
    service: DuplicateDetectionService = Depends(get_service)
):
    """
    Detect potential duplicates for a bug.

    Returns similarity scores for matching bugs.
    """
    try:
        result = service.detect_duplicates(bug_id, program_id, limit)

        return {
            "success": True,
            "query_bug_id": result.query_bug_id,
            "detection_time_ms": result.detection_time_ms,
            "potential_duplicates": [
                {
                    "bug_id": score.bug_id,
                    "title_similarity": score.title_similarity,
                    "description_similarity": score.description_similarity,
                    "code_similarity": score.code_similarity,
                    "url_similarity": score.url_similarity,
                    "overall_score": score.overall_score,
                    "is_duplicate": score.is_duplicate,
                    "confidence": round(score.confidence * 100, 1)
                }
                for score in result.potential_duplicates
            ],
            "highest_match": {
                "bug_id": result.highest_match.bug_id,
                "overall_score": result.highest_match.overall_score,
                "is_duplicate": result.highest_match.is_duplicate
            } if result.highest_match else None
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Detect duplicates failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect/batch", response_model=Dict[str, Any])
async def batch_detect_duplicates(
    bug_ids: List[str],
    program_id: Optional[str] = Query(None, description="Filter by program"),
    service: DuplicateDetectionService = Depends(get_service)
):
    """Run duplicate detection for multiple bugs."""
    try:
        results = service.batch_detect(bug_ids, program_id)

        return {
            "success": True,
            "bugs_checked": len(bug_ids),
            "results": [
                {
                    "query_bug_id": r.query_bug_id,
                    "duplicates_found": len([
                        d for d in r.potential_duplicates if d.is_duplicate
                    ]),
                    "highest_score": r.highest_match.overall_score if r.highest_match else 0
                }
                for r in results
            ]
        }

    except Exception as e:
        logger.error(f"Batch detect failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cluster Analysis Endpoints
@router.get("/clusters", response_model=Dict[str, Any])
async def find_duplicate_clusters(
    program_id: Optional[str] = Query(None, description="Filter by program"),
    threshold: float = Query(0.7, description="Similarity threshold"),
    service: DuplicateDetectionService = Depends(get_service)
):
    """
    Find clusters of duplicate bugs.

    Groups bugs that are mutually similar above threshold.
    """
    try:
        clusters = service.find_duplicate_clusters(program_id, threshold)

        return {
            "success": True,
            "threshold": threshold,
            "clusters_found": len(clusters),
            "clusters": [
                {
                    "cluster_id": i + 1,
                    "bug_count": len(cluster),
                    "bug_ids": cluster
                }
                for i, cluster in enumerate(clusters)
            ]
        }

    except Exception as e:
        logger.error(f"Find clusters failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration Endpoints
@router.put("/thresholds", response_model=Dict[str, Any])
async def update_thresholds(
    request: ThresholdUpdateRequest,
    service: DuplicateDetectionService = Depends(get_service)
):
    """Update similarity detection thresholds."""
    try:
        thresholds = {}
        if request.title is not None:
            thresholds["title"] = request.title
        if request.description is not None:
            thresholds["description"] = request.description
        if request.code is not None:
            thresholds["code"] = request.code
        if request.url is not None:
            thresholds["url"] = request.url
        if request.overall is not None:
            thresholds["overall"] = request.overall

        service.set_thresholds(thresholds)

        return {
            "success": True,
            "message": "Thresholds updated",
            "thresholds": thresholds
        }

    except Exception as e:
        logger.error(f"Update thresholds failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thresholds", response_model=Dict[str, Any])
async def get_thresholds(
    service: DuplicateDetectionService = Depends(get_service)
):
    """Get current detection thresholds."""
    try:
        stats = service.get_statistics()

        return {
            "success": True,
            "thresholds": stats.get("thresholds", {})
        }

    except Exception as e:
        logger.error(f"Get thresholds failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics Endpoints
@router.get("/stats", response_model=Dict[str, Any])
async def get_detection_stats(
    service: DuplicateDetectionService = Depends(get_service)
):
    """Get duplicate detection service statistics."""
    try:
        stats = service.get_statistics()

        return {
            "success": True,
            **stats
        }

    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    service: DuplicateDetectionService = Depends(get_service)
):
    """Duplicate detection service health check."""
    stats = service.get_statistics()

    return {
        "status": "healthy",
        "service": "duplicate_detection",
        "bugs_indexed": stats.get("total_bugs_indexed", 0),
        "unique_terms": stats.get("unique_terms", 0)
    }
