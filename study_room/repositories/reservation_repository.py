# study_room/repositories/reservation_repository.py

from datetime import date, time
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from study_room.models.reservation import Reservation


class ReservationRepository:
    def save(self, db: Session, reservation: Reservation):
        db.add(reservation)
        return reservation

    def find_by_user_id(self, db: Session, user_id: int):
        stmt = (
            select(Reservation)
            .options(joinedload(Reservation.room))
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.reservation_date.desc(), Reservation.start_time.desc())
        )
        return db.scalars(stmt).all()

    def find_by_id(self, db: Session, reservation_id: int):
        stmt = (
            select(Reservation)
            .options(joinedload(Reservation.room))
            .where(Reservation.id == reservation_id)
        )
        return db.scalars(stmt).first()

    def find_conflict(self, db: Session, room_id: int, reservation_date: date, start_time: time):
        """중복 예약 확인"""
        stmt = select(Reservation).where(
            and_(
                Reservation.room_id == room_id,
                Reservation.reservation_date == reservation_date,
                Reservation.start_time == start_time,
                Reservation.status != "취소",
            )
        )
        return db.scalar(stmt)


reservation_repository = ReservationRepository()