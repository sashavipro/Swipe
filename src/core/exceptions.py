"""src/core/exceptions.py."""

from typing import Optional
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class DomainException(Exception):
    """
    Base class for application logic errors.
    Contains default values that can be overridden in subclasses.
    """

    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An internal error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class BadRequestError(DomainException):
    """Error 400: Bad Request (client logic error)."""

    status_code = 400
    code = "BAD_REQUEST"
    message = "Bad request."


class ResourceAlreadyExistsError(DomainException):
    """Error 409: Resource already exists."""

    status_code = 409
    code = "RESOURCE_ALREADY_EXISTS"
    message = "The resource already exists."


class ResourceNotFoundError(DomainException):
    """Error 404: Resource not found."""

    status_code = 404
    code = "RESOURCE_NOT_FOUND"
    message = "The requested resource was not found."


class PermissionDeniedError(DomainException):
    """Error 403: Permission denied."""

    status_code = 403
    code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."


class AuthenticationFailedError(DomainException):
    """Error 401: Authentication failed."""

    status_code = 401
    code = "AUTHENTICATION_FAILED"
    message = "Authentication failed."


class ValidationFailedError(DomainException):
    """Error 422: Invalid data (for manual invocation, not Pydantic)."""

    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Validation failed."


def domain_exception_handler(_request: Request, exc: DomainException):
    """
    Universal handler for all DomainExceptions.
    Takes the code and status directly from the exception class.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
        },
    )


def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic validation errors (422) and converts them to a common format.
    """
    error_messages = []
    for error in exc.errors():
        loc = error.get("loc")
        field = loc[-1] if loc else "unknown"
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


def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    """Intercepts standard FastAPI/Starlette errors
    (e.g., 404 from FastAPI if the path is not found)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
        },
    )


def setup_exception_handlers(app: FastAPI):
    """Registers exception handlers."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
