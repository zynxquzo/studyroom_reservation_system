# study_room/repositories/study_room_repository.py

from datetime import date, time
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_
from study_room.models.study_room import StudyRoom
from study_room.models.reservation import Reservation


class StudyRoomRepository:
    def find_all(self, db: Session, floor: int | None = None, capacity: int | None = None):
        stmt = select(StudyRoom).options(selectinload(StudyRoom.facilities))

        if floor is not None:
            stmt = stmt.where(StudyRoom.floor == floor)
        if capacity is not None:
            stmt = stmt.where(StudyRoom.max_capacity >= capacity)

        return db.scalars(stmt).all()

    def find_by_id(self, db: Session, room_id: int):
        return db.get(StudyRoom, room_id, options=[selectinload(StudyRoom.facilities)])

    def get_reserved_times(self, db: Session, room_id: int, reservation_date: date) -> list[time]:
        """해당 날짜에 예약된 시간 목록 반환"""
        stmt = select(Reservation).where(
            and_(
                Reservation.room_id == room_id,
                Reservation.reservation_date == reservation_date,
                Reservation.status != "취소",
            )
        )
        reservations = db.scalars(stmt).all()
        return [r.start_time for r in reservations]

    def update_rating(self, db: Session, room: StudyRoom, new_rating: float):
        room.rating = new_rating


study_room_repository = StudyRoomRepository()