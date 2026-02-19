# study_room/schemas/review.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReviewCreate(BaseModel):
    reservation_id: int
    rating: float
    content: str | None = None


class ReviewResponse(BaseModel):
    id: int
    room_name: str
    rating: float
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewListItem(BaseModel):
    id: int
    student_id: str  # 마스킹 처리된 학번
    rating: float
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomReviewsResponse(BaseModel):
    room_id: int
    average_rating: float
    reviews: list[ReviewListItem]