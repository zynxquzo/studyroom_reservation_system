# study_room/services/auth_service.py

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from dotenv import load_dotenv

from study_room.repositories.user_repository import user_repository
from study_room.models.user import User
from study_room.schemas.auth import UserCreate, UserLogin

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


class AuthService:
    def _hash_password(self, password: str) -> str:
        """비밀번호를 bcrypt로 해싱한다."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hashed: str) -> bool:
        """입력된 비밀번호와 해시된 비밀번호를 비교한다."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def _create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def signup(self, db: Session, data: UserCreate):
        with db.begin():
            # 1. 학번 중복 검사
            if user_repository.exists_by_student_id(db, data.student_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 등록된 학번입니다.",
                )

            # 2. 비밀번호 해싱 후 저장
            hashed_password = self._hash_password(data.password)
            new_user = User(
                student_id=data.student_id,
                password=hashed_password,
                name=data.name,
            )
            user_repository.save(db, new_user)

        db.refresh(new_user)
        return new_user

    def login(self, db: Session, data: UserLogin) -> str:
        # 1. 학번으로 사용자 조회
        user = user_repository.find_by_student_id(db, data.student_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="학번 또는 비밀번호가 올바르지 않습니다.",
            )

        # 2. 비밀번호 검증
        if not self._verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="학번 또는 비밀번호가 올바르지 않습니다.",
            )

        # 3. JWT 토큰 생성 및 반환
        return self._create_access_token(user.id)

    def get_current_user(self, db: Session, token: str) -> User:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = int(payload.get("sub"))
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다.",
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다.",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
            )

        user = user_repository.find_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
            )
        return user


auth_service = AuthService()