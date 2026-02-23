# study_room/repositories/study_room_repository.py

from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_
from study_room.models.study_room import StudyRoom
from study_room.models.reservation import Reservation


class StudyRoomRepository:
    async def find_all(self, db: AsyncSession, floor: int | None = None, capacity: int | None = None):
        stmt = select(StudyRoom).options(selectinload(StudyRoom.facilities))
        if floor is not None:
            stmt = stmt.where(StudyRoom.floor == floor)
        if capacity is not None:
            stmt = stmt.where(StudyRoom.max_capacity >= capacity)
        result = await db.scalars(stmt)
        return result.all()

    async def find_by_id(self, db: AsyncSession, room_id: int):
        stmt = select(StudyRoom).options(selectinload(StudyRoom.facilities)).where(StudyRoom.room_id == room_id)
        return await db.scalar(stmt)

    async def get_reserved_times(self, db: AsyncSession, room_id: int, reservation_date: date) -> list[time]:
        stmt = select(Reservation).where(
            and_(
                Reservation.room_id == room_id,
                Reservation.reservation_date == reservation_date,
                Reservation.status != "취소",
            )
        )
        result = await db.scalars(stmt)
        return [r.start_time for r in result.all()]

    async def update_rating(self, db: AsyncSession, room: StudyRoom, new_rating: float) -> None:
        """룸 평점을 세션 내에서만 변경. DB 반영은 호출 측에서 같은 트랜잭션을 커밋할 때 이루어짐.
        리뷰 저장과 같은 트랜잭션에서 호출해야 하며(db.begin() 블록 안 등), 다른 서비스에서 재사용 시
        반드시 이 메서드 호출 후 같은 세션으로 commit 해야 반영됨."""
        room.rating = new_rating


study_room_repository = StudyRoomRepository()