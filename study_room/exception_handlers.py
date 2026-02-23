# study_room/exception_handlers.py

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from study_room.exceptions import AppException


logger = logging.getLogger("study_room")


def register_exception_handlers(app: FastAPI) -> None:
    """앱에 예외 핸들러 등록"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        content = {"detail": exc.detail}
        if getattr(exc, "code", None) is not None:
            content["code"] = exc.code
        logger.warning(
            "Business Exception: %s (Path: %s, code=%s)",
            exc.detail,
            request.url.path,
            getattr(exc, "code", None),
        )
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        first_error = errors[0]
        field = " → ".join(str(loc) for loc in first_error["loc"])
        message = first_error["msg"]
        logger.info("Validation Failed: %s - %s: %s", request.url.path, field, message)
        return JSONResponse(
            status_code=422,
            content={"detail": f"{field}: {message}"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("Unexpected Error: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "서버 내부 오류가 발생했습니다."},
        )
