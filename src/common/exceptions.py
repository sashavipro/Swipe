"""src/common/exceptions.py."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


class DomainException(Exception):
    """Базовый класс для логических ошибок приложения."""


class ResourceAlreadyExistsError(DomainException):
    """Ошибка: Ресурс уже существует (например, дубликат)."""


class ResourceNotFoundError(DomainException):
    """Ошибка: Ресурс не найден."""


class PermissionDeniedError(DomainException):
    """Ошибка: Недостаточно прав для выполнения операции."""


class AuthenticationFailedError(DomainException):
    """Ошибка: Неверный логин/пароль или токен (401)."""


def resource_exists_handler(_request: Request, exc: ResourceAlreadyExistsError):
    """Перехватывает ошибки дубликатов."""
    return JSONResponse(
        status_code=409,
        content={
            "status": "error",
            "code": "RESOURCE_ALREADY_EXISTS",
            "message": str(exc),
        },
    )


def resource_not_found_handler(_request: Request, exc: ResourceNotFoundError):
    """Перехватывает ошибки 'не найдено'."""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "code": "RESOURCE_NOT_FOUND",
            "message": str(exc),
        },
    )


def permission_denied_handler(_request: Request, exc: PermissionDeniedError):
    """Перехватывает ошибки доступа."""
    return JSONResponse(
        status_code=403,
        content={
            "status": "error",
            "code": "PERMISSION_DENIED",
            "message": str(exc),
        },
    )


def authentication_failed_handler(_request: Request, exc: AuthenticationFailedError):
    """Перехватывает ошибки аутентификации."""
    return JSONResponse(
        status_code=401,
        content={
            "status": "error",
            "code": "AUTHENTICATION_FAILED",
            "message": str(exc),
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_exception_handler(_request: Request, exc: HTTPException):
    """Перехватывает стандартные ошибки FastAPI/Starlette."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
        },
    )


def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """
    Перехватывает ошибки валидации Pydantic (422).
    Превращает их в единый стиль.
    """
    error_messages = []
    for error in exc.errors():
        field = error.get("loc")[-1] if error.get("loc") else "unknown"
        msg = error.get("msg")
        error_messages.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "; ".join(error_messages),
        },
    )


def setup_exception_handlers(app: FastAPI):
    """Регистрирует все обработчики ошибок в приложении."""
    app.add_exception_handler(ResourceAlreadyExistsError, resource_exists_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
    app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
    app.add_exception_handler(AuthenticationFailedError, authentication_failed_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
