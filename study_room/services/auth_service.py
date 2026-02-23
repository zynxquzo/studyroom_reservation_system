# study_room/services/auth_service.py

import os
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from study_room.exceptions import UnauthorizedException, DuplicateException
from study_room.repositories.user_repository import user_repository
from study_room.models.user import User
from study_room.schemas.auth import UserCreate, UserLogin

logger = logging.getLogger(__name__)

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
        """회원가입. 트랜잭션 규칙: db.begin() 블록 안에서만 쓰기 후, 블록 탈출 시 자동 커밋.
        refresh는 의도적으로 블록 밖에서 수행(커밋 후 DB 반영값(id 등)을 new_user에 채우기 위함)."""
        logger.info("회원가입 시도: student_id=%s", data.student_id)
        async with db.begin():
            if await user_repository.exists_by_student_id(db, data.student_id):
                logger.warning("회원가입 실패 - 학번 중복: %s", data.student_id)
                raise DuplicateException("이미 등록된 학번입니다.")
            hashed_password = self._hash_password(data.password)
            new_user = User(
                student_id=data.student_id,
                password=hashed_password,
                name=data.name,
            )
            await user_repository.save(db, new_user)

        await db.refresh(new_user)
        logger.info("회원가입 성공: user_id=%s, student_id=%s", new_user.id, new_user.student_id)
        return new_user

    async def login(self, db: AsyncSession, data: UserLogin) -> str:
        logger.info("로그인 시도: student_id=%s", data.student_id)
        user = await user_repository.find_by_student_id(db, data.student_id)
        if not user:
            logger.warning("로그인 실패 - 존재하지 않는 학번: %s", data.student_id)
            raise UnauthorizedException("학번 또는 비밀번호가 올바르지 않습니다.", code="invalid_credentials")
        if not self._verify_password(data.password, user.password):
            logger.warning("로그인 실패 - 잘못된 비밀번호: student_id=%s", data.student_id)
            raise UnauthorizedException("학번 또는 비밀번호가 올바르지 않습니다.", code="invalid_credentials")
        token = self._create_access_token(user.id)
        logger.info("로그인 성공: user_id=%s", user.id)
        return token

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_raw = payload.get("sub")
            if user_id_raw is None:
                raise UnauthorizedException("유효하지 않은 토큰입니다.", code="invalid_token")
            user_id = int(user_id_raw)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("토큰이 만료되었습니다. 다시 로그인해 주세요.", code="token_expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("유효하지 않은 토큰입니다.", code="invalid_token")

        user = await user_repository.find_by_id(db, user_id)
        if not user:
            raise UnauthorizedException("사용자를 찾을 수 없습니다.", code="user_not_found")
        return user


auth_service = AuthService()
