"""src/common/schemas.py."""

import re
from pydantic import BaseModel, field_validator


class PhoneSchemaMixin(BaseModel):
    """
    Миксин для валидации поля 'phone'.
    Подключается к любой схеме, где есть поле phone (обязательное или опциональное).
    """

    @field_validator("phone", check_fields=False)
    @classmethod
    def validate_phone_format(cls, v: str | None) -> str | None:
        """
        Очищает и проверяет формат телефона.
        """
        if v is None:
            return None

        if not v:
            return v

        clean_phone = re.sub(r"[\s\-\(\)]", "", v)

        if not re.match(r"^\+?\d{7,15}$", clean_phone):
            raise ValueError("Invalid phone number format. Must contain 7-15 digits.")

        return clean_phone
