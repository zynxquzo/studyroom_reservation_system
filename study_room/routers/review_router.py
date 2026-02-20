# study_room/routers/review_router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from async_database import get_async_db
from study_room.services.review_service import review_service
from study_room.schemas.review import ReviewCreate, ReviewResponse
from study_room.dependencies import get_current_user
from study_room.models.user import User

router = APIRouter(prefix="/reviews", tags=["Review"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await review_service.create_review(db, data, current_user)