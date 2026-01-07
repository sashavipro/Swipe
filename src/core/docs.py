"""src/core/docs.py."""

from typing import Any, Dict, Type

from src.core.exceptions import DomainException
from src.core.schemas.response import ErrorResponse


def create_error_responses(
    *exceptions: Type[DomainException],
) -> Dict[int, Dict[str, Any]]:
    """
    Generates a dictionary of responses for FastAPI swagger based on the passed exception classes.

    Usage example:
    responses=create_error_responses(ResourceNotFoundError, PermissionDeniedError)
    """
    responses = {}

    for exc_class in exceptions:
        status_code = exc_class.status_code
        code = exc_class.code
        message = exc_class.message

        example = {"status": "error", "code": code, "message": message}

        responses[status_code] = {
            "model": ErrorResponse,
            "description": f"{code}: {message}",
            "content": {"application/json": {"example": example}},
        }

    return responses


VALIDATION_ERROR_RESPONSE = {
    "description": "Validation Error",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status": "error",
                "code": "VALIDATION_ERROR",
                "message": "field_name: Error description; another_field: Error description",
            }
        }
    },
}
