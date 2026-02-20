# study_room/repositories/user_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from study_room.models.user import User


class UserRepository:
    async def save(self, db: AsyncSession, user: User):
        db.add(user)
        return user

    async def find_by_student_id(self, db: AsyncSession, student_id: str):
        stmt = select(User).where(User.student_id == student_id)
        return await db.scalar(stmt)

    async def find_by_id(self, db: AsyncSession, user_id: int):
        return await db.get(User, user_id)

    async def exists_by_student_id(self, db: AsyncSession, student_id: str) -> bool:
        stmt = select(User).where(User.student_id == student_id)
        return await db.scalar(stmt) is not None


user_repository = UserRepository()