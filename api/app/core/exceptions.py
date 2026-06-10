from __future__ import annotations
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

class AuthException(Exception):

    def __init__(self, detail: str = "Authentication failed.", code: str = "AUTH_FAILED") -> None:
        self.detail = detail
        self.code = code
        super().__init__(detail)


class ConflictException(Exception):

    def __init__(self, detail: str = "Resource already exists.", code: str = "CONFLICT") -> None:
        self.detail = detail
        self.code = code
        super().__init__(detail)


class ForbiddenException(Exception):

    def __init__(self, detail: str = "Access forbidden.", code: str = "FORBIDDEN") -> None:
        self.detail = detail
        self.code = code
        super().__init__(detail)


class NotFoundException(Exception):

    def __init__(self, detail: str = "Resource not found.", code: str = "NOT_FOUND") -> None:
        self.detail = detail
        self.code = code
        super().__init__(detail)


class OAuthException(Exception):

    def __init__(self, detail: str, code: str, status_code: int = 400) -> None:
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)




def _error_body(error: str, detail: str, code: str) -> dict:
    return {"error": error, "detail": detail, "code": code}



async def oauth_exception_handler(request: Request, exc: OAuthException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "oauth_error", "code": exc.code, "detail": exc.detail},
    )


async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=_error_body("Unauthorized", exc.detail, exc.code),
        headers={"WWW-Authenticate": "Bearer"},
    )


async def conflict_exception_handler(request: Request, exc: ConflictException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error_body("Conflict", exc.detail, exc.code),
    )


async def forbidden_exception_handler(request: Request, exc: ForbiddenException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=_error_body("Forbidden", exc.detail, exc.code),
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_error_body("Not Found", exc.detail, exc.code),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:

    code_map = {
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    error_name = {
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }.get(exc.status_code, "Error")

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(error_name, str(exc.detail), code),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:

    errors = exc.errors()
    first = errors[0] if errors else {}
    field = " → ".join(str(loc) for loc in first.get("loc", [])) if first else "unknown"
    msg = first.get("msg", "Validation error") if first else "Validation error"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body(
            "Validation Error",
            f"Field '{field}': {msg}",
            "VALIDATION_ERROR",
        ),
    )




def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(OAuthException, oauth_exception_handler)
    app.add_exception_handler(AuthException, auth_exception_handler)
    app.add_exception_handler(ConflictException, conflict_exception_handler)
    app.add_exception_handler(ForbiddenException, forbidden_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
