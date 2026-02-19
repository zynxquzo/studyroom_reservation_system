from fastapi import FastAPI
from database import engine, Base
from study_room.routers.auth_router import router as auth_router
from study_room.routers.reservation_router import router as reservation_router
from study_room.routers.review_router import router as review_router
from study_room.routers.study_room_router import router as study_room_router
# from mysite4.models.post import Post  # 모델 파일이 import되어야 Base가 인식한다.

# 기존 테이블 지우기
# Base.metadata.drop_all(bind=engine)

# 정의된 모델들을 기반으로 DB에 테이블을 생성한다.
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router) 
app.include_router(reservation_router) 
app.include_router(review_router) 
app.include_router(study_room_router) 

@app.get("/")
def read_root():
    return {"Hello": "World"}