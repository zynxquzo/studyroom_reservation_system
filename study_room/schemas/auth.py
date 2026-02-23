# study_room/schemas/auth.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """DB 컬럼 길이와 맞춰 검증 (student_id 20, password 200, name 50). DB 오류 전에 검증됨."""

    student_id: str = Field(..., min_length=1, max_length=20, description="학번")
    password: str = Field(..., min_length=1, max_length=200, description="비밀번호")
    name: str = Field(..., min_length=1, max_length=50, description="이름")


class UserResponse(BaseModel):
    id: int
    student_id: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=20, description="학번")
    password: str = Field(..., min_length=1, max_length=200, description="비밀번호")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"