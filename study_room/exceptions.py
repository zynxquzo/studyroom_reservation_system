# study_room/exceptions.py
# 인증 실패 시 클라이언트가 "재로그인 유도"(token_expired) vs "토큰 형식 오류"(invalid_token)를
# 구분할 수 있도록 UnauthorizedException에 code를 사용함.


class AppException(Exception):
    """앱 전체 예외의 부모 클래스"""

    status_code: int = 500

    def __init__(self, detail: str, code: str | None = None):
        self.detail = detail
        self.code = code


class BadRequestException(AppException):
    """잘못된 요청 (400)"""
    status_code = 400


class UnauthorizedException(AppException):
    """인증 실패 (401). code 예: token_expired(재로그인 유도), invalid_token(토큰 형식 오류), invalid_credentials, user_not_found"""
    status_code = 401


class ForbiddenException(AppException):
    """권한 없음 (403)"""
    status_code = 403


class NotFoundException(AppException):
    """리소스를 찾을 수 없을 때 (404)"""
    status_code = 404


class DuplicateException(AppException):
    """중복/충돌 (409)"""
    status_code = 409
