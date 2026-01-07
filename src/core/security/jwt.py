"""src/core/security/jwt.py."""

from datetime import datetime, timedelta, timezone
from typing import Literal

# Pylint confuses this file (jwt.py) with the jwt library, so we disable checks
# pylint: disable=import-self, no-member
import jwt
from src.core.config import settings


class JWTHandler:
    """
    Utility for working with JWT tokens (encoding and decoding).
    """

    @staticmethod
    def create_token(
        data: dict, token_type: Literal["access", "refresh"], expires_delta: timedelta
    ) -> str:
        """
        Creates a JWT token with the specified type and lifetime.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode.update({"exp": expire, "type": token_type})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        Generates Access Token.
        """
        return JWTHandler.create_token(
            data, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Generates Refresh Token.
        """
        return JWTHandler.create_token(
            data, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

    @staticmethod
    def decode_token(token: str) -> dict | None:
        """
        Decodes the token. Returns payload or None if the token is invalid.
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
        Generates a token confirming ownership of the number.
        Lives for a short time (15 minutes).
        """
        return JWTHandler.create_token(
            data={"sub": phone},
            token_type="verification_phone",
            expires_delta=timedelta(minutes=15),
        )

    @staticmethod
    def create_reset_password_token(email: str) -> str:
        """
        Generates a token for password reset.
        Lifetime: 30 minutes.
        """
        return JWTHandler.create_token(
            data={"sub": email},
            token_type="reset_password",
            expires_delta=timedelta(minutes=30),
        )
