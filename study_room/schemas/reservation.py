# study_room/schemas/reservation.py

from datetime import date
from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    room_id: int
    reservation_date: date
    start_time: str  # "14:00" 형태


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