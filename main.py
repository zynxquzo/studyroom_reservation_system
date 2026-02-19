from fastapi import FastAPI
from database import engine, Base
# from mysite4.models.post import Post  # 모델 파일이 import되어야 Base가 인식한다.

# 기존 테이블 지우기
# Base.metadata.drop_all(bind=engine)

# 정의된 모델들을 기반으로 DB에 테이블을 생성한다.
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}