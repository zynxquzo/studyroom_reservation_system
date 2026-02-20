# study_room/routers/auth_router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from async_database import get_async_db
from study_room.services.auth_service import auth_service
from study_room.schemas.auth import UserCreate, UserResponse, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_async_db)):
    return await auth_service.signup(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    access_token = await auth_service.login(db, data)
    return {"access_token": access_token}