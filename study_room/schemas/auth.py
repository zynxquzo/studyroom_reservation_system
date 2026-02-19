# study_room/schemas/auth.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    student_id: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: int
    student_id: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    student_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"