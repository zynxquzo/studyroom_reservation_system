# study_room/repositories/review_repository.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from study_room.models.review import Review


class ReviewRepository:
    def save(self, db: Session, review: Review):
        db.add(review)
        return review

    def find_by_room_id(self, db: Session, room_id: int):
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.room_id == room_id)
            .order_by(Review.created_at.desc())
        )
        return db.scalars(stmt).all()

    def find_by_reservation_id(self, db: Session, reservation_id: int):
        stmt = select(Review).where(Review.reservation_id == reservation_id)
        return db.scalar(stmt)

    def get_average_rating(self, db: Session, room_id: int) -> float:
        result = db.scalar(select(func.avg(Review.rating)).where(Review.room_id == room_id))
        return round(float(result), 1) if result else 0.0


review_repository = ReviewRepository()