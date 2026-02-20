# study_room/repositories/review_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from study_room.models.review import Review


class ReviewRepository:
    async def save(self, db: AsyncSession, review: Review):
        db.add(review)
        return review

    async def find_by_room_id(self, db: AsyncSession, room_id: int):
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.room_id == room_id)
            .order_by(Review.created_at.desc())
        )
        result = await db.scalars(stmt)
        return result.all()

    async def find_by_reservation_id(self, db: AsyncSession, reservation_id: int):
        stmt = select(Review).where(Review.reservation_id == reservation_id)
        return await db.scalar(stmt)

    async def get_average_rating(self, db: AsyncSession, room_id: int) -> float:
        result = await db.scalar(select(func.avg(Review.rating)).where(Review.room_id == room_id))
        return round(float(result), 1) if result else 0.0


review_repository = ReviewRepository()