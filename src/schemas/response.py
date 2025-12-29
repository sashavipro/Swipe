"""src/schemas/response.py."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error response schema.
    """

    status: str = Field(example="error", description="Response status")
    code: str = Field(
        example="RESOURCE_NOT_FOUND", description="Error code for frontend"
    )
    message: str = Field(
        example="User with id 123 not found", description="Human-readable message"
    )
