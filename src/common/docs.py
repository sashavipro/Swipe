"""src/core/docs.py."""

from typing import Any, Dict
from src.schemas.response import ErrorResponse


def create_error_responses(*status_codes: int) -> Dict[int, Dict[str, Any]]:
    """
    Генерирует словарь responses для FastAPI swagger.
    Принимает список кодов (401, 403, 404 и т.д.).
    """
    responses = {}

    # Описания стандартных ошибок
    descriptions = {
        400: "Bad Request - Некорректный запрос",
        401: "Unauthorized - Неверный токен или логин/пароль",
        403: "Forbidden - Недостаточно прав (например, вы не модератор)",
        404: "Not Found - Ресурс не найден",
        409: "Conflict - Дубликат данных (email/телефон уже занят)",
        422: "Validation Error - Ошибка валидации данных",
    }

    # Примеры кодов ошибок для документации
    examples = {
        400: {"status": "error", "code": "BAD_REQUEST", "message": "Invalid data"},
        401: {
            "status": "error",
            "code": "AUTHENTICATION_FAILED",
            "message": "Invalid token",
        },
        403: {
            "status": "error",
            "code": "PERMISSION_DENIED",
            "message": "Only moderators can perform this action",
        },
        404: {
            "status": "error",
            "code": "RESOURCE_NOT_FOUND",
            "message": "User not found",
        },
        409: {
            "status": "error",
            "code": "RESOURCE_ALREADY_EXISTS",
            "message": "Email already taken",
        },
        422: {
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "phone: Invalid format; email: value is not a valid email address",
        },
    }

    for code in status_codes:
        responses[code] = {
            "model": ErrorResponse,
            "description": descriptions.get(code, "Error"),
            "content": {"application/json": {"example": examples.get(code, {})}},
        }

    return responses
