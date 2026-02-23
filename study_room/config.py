# study_room/config.py
# 서버 기동 시점에 필수 환경 변수를 검사하여, 없으면 명시적 예외를 던짐 (운영 디버깅 용이).

import os

from dotenv import load_dotenv

load_dotenv(encoding="utf-8")

REQUIRED_ENV_KEYS = [
    "JWT_SECRET_KEY",
    "DATABASE_URL",
]


def validate_required_env() -> None:
    """필수 환경 변수가 모두 설정되었는지 검사. 없으면 ValueError를 던짐."""
    missing = [key for key in REQUIRED_ENV_KEYS if not (os.getenv(key) or "").strip()]
    if missing:
        raise ValueError(
            f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing)}. "
            ".env 파일 또는 환경 변수를 확인하세요."
        )
