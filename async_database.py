import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv()

SYNC_DATABASE_URL = os.getenv("DATABASE_URL")
ASYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# echo=True 시 SQL 로그 출력 → 개발 시 유용, 운영에서는 로그 양·비밀번호 노출 우려로 끄는 것이 좋음
_echo = os.getenv("DATABASE_ECHO", "").lower() in ("1", "true", "yes")
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=_echo)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session