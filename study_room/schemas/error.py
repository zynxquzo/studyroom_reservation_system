# study_room/schemas/error.py

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"detail": "에러 메시지"},
                {"detail": "토큰이 만료되었습니다.", "code": "token_expired"},
                {"detail": "유효하지 않은 토큰입니다.", "code": "invalid_token"},
            ]
        }
    }
