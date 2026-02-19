# study_room/routers/study_room_router.py

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from study_room.services.study_room_service import study_room_service
from study_room.services.review_service import review_service
from study_room.schemas.study_room import StudyRoomListResponse, StudyRoomDetailResponse, AvailableTimesResponse
from study_room.schemas.review import RoomReviewsResponse

router = APIRouter(prefix="/rooms", tags=["StudyRoom"])


@router.get("", response_model=list[StudyRoomListResponse])
def read_rooms(
    floor: int | None = Query(None, description="층 필터 (4 또는 5)"),
    capacity: int | None = Query(None, description="최소 수용 인원"),
    db: Session = Depends(get_db),
):
    """스터디룸 목록 조회"""
    return study_room_service.read_rooms(db, floor=floor, capacity=capacity)


@router.get("/{room_id}", response_model=StudyRoomDetailResponse)
def read_room(room_id: int, db: Session = Depends(get_db)):
    """스터디룸 상세 조회"""
    return study_room_service.read_room_detail(db, room_id)


@router.get("/{room_id}/available-times", response_model=AvailableTimesResponse)
def read_available_times(
    room_id: int,
    date: date = Query(..., description="조회할 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """예약 가능 시간 조회"""
    return study_room_service.read_available_times(db, room_id, date)


@router.get("/{room_id}/reviews", response_model=RoomReviewsResponse)
def read_room_reviews(room_id: int, db: Session = Depends(get_db)):
    """스터디룸 리뷰 목록 조회"""
    return review_service.read_room_reviews(db, room_id)