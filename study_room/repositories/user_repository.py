# study_room/repositories/user_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from study_room.models.user import User


class UserRepository:
    def save(self, db: Session, user: User):
        db.add(user)
        return user

    def find_by_student_id(self, db: Session, student_id: str):
        stmt = select(User).where(User.student_id == student_id)
        return db.scalars(stmt).first()

    def find_by_id(self, db: Session, user_id: int):
        return db.get(User, user_id)

    def exists_by_student_id(self, db: Session, student_id: str) -> bool:
        stmt = select(User).where(User.student_id == student_id)
        return db.scalar(stmt) is not None


user_repository = UserRepository()