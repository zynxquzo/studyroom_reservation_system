# study_room/models/study_room.py

from datetime import time
from sqlalchemy import String, Float, Time, Table, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .reservation import Reservation
    from .review import Review


# 스터디룸 - 시설 중간 테이블 (M:N)
room_facility_map = Table(
    "room_facility_map",
    Base.metadata,
    mapped_column("room_id", Integer, ForeignKey("study_rooms.room_id"), primary_key=True),
    mapped_column("facility_id", Integer, ForeignKey("facilities.facility_id"), primary_key=True),
)


class StudyRoom(Base):
    __tablename__ = "study_rooms"

    room_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    floor: Mapped[int] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    max_capacity: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)

    facilities: Mapped[list["Facility"]] = relationship(
        secondary=room_facility_map, back_populates="rooms"
    )
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="room")
    reviews: Mapped[list["Review"]] = relationship(back_populates="room")


class Facility(Base):
    __tablename__ = "facilities"

    facility_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    rooms: Mapped[list["StudyRoom"]] = relationship(
        secondary=room_facility_map, back_populates="facilities"
    )