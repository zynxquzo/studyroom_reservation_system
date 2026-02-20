from fastapi import FastAPI
from contextlib import asynccontextmanager

from async_database import async_engine
from study_room import models

from study_room.routers.auth_router import router as auth_router
from study_room.routers.study_room_router import router as study_room_router
from study_room.routers.reservation_router import router as reservation_router
from study_room.routers.review_router import router as review_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시: 테이블 생성
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # 서버 종료 시: 엔진 정리
    await async_engine.dispose()


app = FastAPI(
    title="스터디룸 예약 시스템",
    description="도서관 스터디룸 예약 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(study_room_router)
app.include_router(reservation_router)
app.include_router(review_router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "스터디룸 예약 시스템이 실행 중입니다."}