# study_room/schemas/study_room.py

from datetime import time
from pydantic import BaseModel, ConfigDict


class FacilityResponse(BaseModel):
    facility_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StudyRoomListResponse(BaseModel):
    room_id: int
    name: str
    floor: int
    location: str
    max_capacity: int
    rating: float
    facilities: list[str]

    model_config = ConfigDict(from_attributes=True)


class StudyRoomDetailResponse(BaseModel):
    room_id: int
    name: str
    floor: int
    location: str
    max_capacity: int
    rating: float
    open_time: time
    close_time: time
    facilities: list[str]

    model_config = ConfigDict(from_attributes=True)


class AvailableTimeSlot(BaseModel):
    time: str
    available: bool


class AvailableTimesResponse(BaseModel):
    room_id: int
    date: str
    available_times: list[AvailableTimeSlot]