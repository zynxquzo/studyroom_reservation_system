# study_room/models/reservation.py

from datetime import date, time, datetime
from sqlalchemy import String, Date, Time, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .study_room import StudyRoom
    from .review import Review


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("study_rooms.room_id"), nullable=False)
    reservation_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    # 예약확정 / 이용완료 / 취소
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="예약확정")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 같은 룸, 같은 날, 같은 시간 중복 예약 방지
    __table_args__ = (
        UniqueConstraint("room_id", "reservation_date", "start_time", name="uq_room_date_time"),
    )

    user: Mapped["User"] = relationship(back_populates="reservations")
    room: Mapped["StudyRoom"] = relationship(back_populates="reservations")
    review: Mapped["Review"] = relationship(back_populates="reservation", uselist=False)