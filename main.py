from fastapi import FastAPI

from database import engine
from study_room import models  

from study_room.routers.auth_router import router as auth_router
from study_room.routers.study_room_router import router as study_room_router
from study_room.routers.reservation_router import router as reservation_router
from study_room.routers.review_router import router as review_router

# 기존 테이블 지우기
# models.Base.metadata.drop_all(bind=engine) # 모델 파일이 import되어야 Base가 인식한다

# 정의된 모델들을 기반으로 DB에 테이블을 생성한다.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="스터디룸 예약 시스템",
    description="도서관 스터디룸 예약 API",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(study_room_router)
app.include_router(reservation_router)
app.include_router(review_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "스터디룸 예약 시스템이 실행 중입니다."}