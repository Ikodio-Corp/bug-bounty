"""
Courses routes - Educational content and certifications
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User

router = APIRouter()
security = Security()


@router.get("/")
async def list_courses(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List courses"""
    # TODO: Implement course listing
    return {"message": "Course catalog"}


@router.get("/{course_id}")
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get course details"""
    # TODO: Implement course retrieval
    return {"message": f"Course {course_id}"}


@router.post("/{course_id}/enroll")
async def enroll_in_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Enroll in course"""
    # TODO: Implement course enrollment
    return {"message": f"Enrolled in course {course_id}"}


@router.post("/create")
async def create_course(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Create course"""
    # TODO: Implement course creation
    return {"message": "Course created"}
