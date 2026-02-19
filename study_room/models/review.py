# study_room/models/review.py

from datetime import datetime
from sqlalchemy import Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .study_room import StudyRoom
    from .reservation import Reservation


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id"), unique=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("study_rooms.room_id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    content: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    reservation: Mapped["Reservation"] = relationship(back_populates="review")
    user: Mapped["User"] = relationship(back_populates="reviews")
    room: Mapped["StudyRoom"] = relationship(back_populates="reviews")