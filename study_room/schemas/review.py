# study_room/schemas/review.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    reservation_id: int
    rating: float = Field(ge=1, le=5, description="별점 (1.0 ~ 5.0)")
    content: str = Field(min_length=10, max_length=500, description="리뷰 내용 (10자 이상)")


class ReviewResponse(BaseModel):
    id: int
    room_name: str
    rating: float
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewListItem(BaseModel):
    id: int
    student_id: str
    rating: float
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomReviewsResponse(BaseModel):
    room_id: int
    average_rating: float
    reviews: list[ReviewListItem]