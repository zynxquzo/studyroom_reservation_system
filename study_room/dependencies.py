# study_room/dependencies.py

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from study_room.services.auth_service import auth_service
from study_room.models.user import User

# Authorization 헤더에서 Bearer 토큰을 자동으로 추출한다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    return auth_service.get_current_user(db, token)