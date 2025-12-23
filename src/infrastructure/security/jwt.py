"""src/infrastructure/security/jwt.py."""

from datetime import datetime, timedelta, timezone
from typing import Literal

# Pylint путает этот файл (jwt.py) с библиотекой jwt, поэтому отключаем проверки
# pylint: disable=import-self, no-member
import jwt
from src.config import settings


class JWTHandler:
    """
    Утилита для работы с JWT токенами (кодирование и декодирование).
    """

    @staticmethod
    def create_token(
        data: dict, token_type: Literal["access", "refresh"], expires_delta: timedelta
    ) -> str:
        """
        Создает JWT токен с указанным типом и временем жизни.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta

        # Добавляем тип токена, чтобы рефреш нельзя было использовать вместо аксесса
        to_encode.update({"exp": expire, "type": token_type})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        Генерирует Access Token.
        """
        return JWTHandler.create_token(
            data, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Генерирует Refresh Token.
        """
        return JWTHandler.create_token(
            data, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

    @staticmethod
    def decode_token(token: str) -> dict | None:
        """
        Декодирует токен. Возвращает payload или None, если токен невалиден.
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def create_verification_token(phone: str) -> str:
        """
        Генерирует токен, подтверждающий владение номером.
        Живет короткое время (15 минут).
        """
        return JWTHandler.create_token(
            data={"sub": phone},
            token_type="verification_phone",
            expires_delta=timedelta(minutes=15),
        )

    @staticmethod
    def create_reset_password_token(email: str) -> str:
        """
        Генерирует токен для сброса пароля.
        Срок жизни: 30 минут.
        """
        return JWTHandler.create_token(
            data={"sub": email},
            token_type="reset_password",
            expires_delta=timedelta(minutes=30),
        )
