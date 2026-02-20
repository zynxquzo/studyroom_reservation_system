# study_room/services/auth_service.py

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from dotenv import load_dotenv

from study_room.repositories.user_repository import user_repository
from study_room.models.user import User
from study_room.schemas.auth import UserCreate, UserLogin

load_dotenv(encoding="utf-8")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


class AuthService:
    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def _create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def signup(self, db: AsyncSession, data: UserCreate):
        async with db.begin():
            if await user_repository.exists_by_student_id(db, data.student_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 등록된 학번입니다.",
                )
            hashed_password = self._hash_password(data.password)
            new_user = User(
                student_id=data.student_id,
                password=hashed_password,
                name=data.name,
            )
            await user_repository.save(db, new_user)

        await db.refresh(new_user)
        return new_user

    async def login(self, db: AsyncSession, data: UserLogin) -> str:
        user = await user_repository.find_by_student_id(db, data.student_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="학번 또는 비밀번호가 올바르지 않습니다.",
            )
        if not self._verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="학번 또는 비밀번호가 올바르지 않습니다.",
            )
        return self._create_access_token(user.id)

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = int(payload.get("sub"))
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")

        user = await user_repository.find_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다.")
        return user


auth_service = AuthService()