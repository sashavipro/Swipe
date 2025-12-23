"""src/schemas/response.py."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Стандартная схема ответа при ошибке.
    """

    status: str = Field(example="error", description="Статус ответа")
    code: str = Field(
        example="RESOURCE_NOT_FOUND", description="Код ошибки для фронтенда"
    )
    message: str = Field(
        example="User with id 123 not found", description="Человекочитаемое сообщение"
    )
