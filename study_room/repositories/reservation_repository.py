# study_room/repositories/reservation_repository.py

from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update, and_, or_, func
from study_room.models.reservation import Reservation


class ReservationRepository:
    async def save(self, db: AsyncSession, reservation: Reservation):
        db.add(reservation)
        return reservation

    async def find_by_user_id(self, db: AsyncSession, user_id: int):
        stmt = (
            select(Reservation)
            .options(joinedload(Reservation.room))
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.reservation_date.desc(), Reservation.start_time.desc())
        )
        result = await db.scalars(stmt)
        return result.all()

    async def find_by_id(self, db: AsyncSession, reservation_id: int):
        stmt = (
            select(Reservation)
            .options(joinedload(Reservation.room))
            .where(Reservation.id == reservation_id)
        )
        return await db.scalar(stmt)

    async def find_conflict(self, db: AsyncSession, room_id: int, reservation_date: date, start_time: time):
        stmt = select(Reservation).where(
            and_(
                Reservation.room_id == room_id,
                Reservation.reservation_date == reservation_date,
                Reservation.start_time == start_time,
                Reservation.status != "취소",
            )
        )
        return await db.scalar(stmt)

    async def count_by_user_and_date(self, db: AsyncSession, user_id: int, res_date: date) -> int:
        stmt = select(func.count()).select_from(Reservation).where(
            Reservation.user_id == user_id,
            Reservation.reservation_date == res_date,
            Reservation.status == "예약확정",
        )
        return await db.scalar(stmt) or 0
    
    async def find_user_conflict(self, db: AsyncSession, user_id: int, reservation_date: date, start_time: time):
        """같은 유저가 같은 날 같은 시간에 다른 방을 예약했는지 확인"""
        stmt = select(Reservation).where(
            and_(
                Reservation.user_id == user_id,
                Reservation.reservation_date == reservation_date,
                Reservation.start_time == start_time,
                Reservation.status != "취소",
            )
        )
        return await db.scalar(stmt)

    async def mark_ended_as_used(
        self, db: AsyncSession, user_id: int, today: date, current_time: time
    ) -> None:
        """이용 종료된 '예약확정' 건만 한 번에 '이용완료'로 전환. 동시성 이슈 완화용 단일 UPDATE."""
        stmt = (
            update(Reservation)
            .where(Reservation.user_id == user_id)
            .where(Reservation.status == "예약확정")
            .where(
                or_(
                    Reservation.reservation_date < today,
                    and_(
                        Reservation.reservation_date == today,
                        Reservation.end_time <= current_time,
                    ),
                )
            )
            .values(status="이용완료")
        )
        await db.execute(stmt)


reservation_repository = ReservationRepository()