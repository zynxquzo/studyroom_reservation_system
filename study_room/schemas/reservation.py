# study_room/schemas/reservation.py

from datetime import date
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


# HH:MM (00:00 ~ 23:59) 형식
START_TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d$")


class ReservationCreate(BaseModel):
    room_id: int
    reservation_date: date
    start_time: str = Field(
        ...,
        description="시작 시간 HH:MM (예: 14:00)",
        min_length=5,
        max_length=5,
    )

    @field_validator("start_time")
    @classmethod
    def validate_start_time_format(cls, v: str) -> str:
        if not START_TIME_PATTERN.fullmatch(v):
            raise ValueError("시간은 HH:MM 형식이어야 합니다 (예: 09:00, 23:00). 00:00~23:59만 가능합니다.")
        return v


class ReservationResponse(BaseModel):
    id: int
    room_name: str
    reservation_date: date
    start_time: str
    end_time: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class MyReservationsResponse(BaseModel):
    reservations: list[ReservationResponse]