# study_room/routers/study_room_router.py

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from async_database import get_async_db
from study_room.services.study_room_service import study_room_service
from study_room.services.review_service import review_service
from study_room.schemas.study_room import StudyRoomListResponse, StudyRoomDetailResponse, AvailableTimesResponse
from study_room.schemas.review import RoomReviewsResponse

router = APIRouter(prefix="/rooms", tags=["StudyRoom"])


@router.get("", response_model=list[StudyRoomListResponse])
async def read_rooms(
    floor: int | None = Query(None, description="층 필터 (4 또는 5)"),
    capacity: int | None = Query(None, description="최소 수용 인원"),
    db: AsyncSession = Depends(get_async_db),
):
    return await study_room_service.read_rooms(db, floor=floor, capacity=capacity)


@router.get("/{room_id}", response_model=StudyRoomDetailResponse)
async def read_room(room_id: int, db: AsyncSession = Depends(get_async_db)):
    return await study_room_service.read_room_detail(db, room_id)


@router.get("/{room_id}/available-times", response_model=AvailableTimesResponse)
async def read_available_times(
    room_id: int,
    date: date = Query(..., description="조회할 날짜 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db),
):
    return await study_room_service.read_available_times(db, room_id, date)


@router.get("/{room_id}/reviews", response_model=RoomReviewsResponse)
async def read_room_reviews(room_id: int, db: AsyncSession = Depends(get_async_db)):
    return await review_service.read_room_reviews(db, room_id)