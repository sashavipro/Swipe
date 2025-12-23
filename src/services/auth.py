"""src/services/auth.py."""

import logging
import random
from datetime import timedelta

from redis.asyncio import Redis
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import (
    ResourceAlreadyExistsError,
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from src.repositories.users import UserRepository
from src.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    VerificationTokenResponse,
    ResetPasswordRequest,
)
from src.infrastructure.security.password import PasswordHandler
from src.infrastructure.security.jwt import JWTHandler
from src.models.users import User, UserRole
from src.worker import send_email_task

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

USER_NOT_FOUND = "User not found"
INVALID_TOKEN_TYPE = "Invalid token type"


class AuthService:
    """
    Сервис аутентификации и авторизации.
    Отвечает за регистрацию, вход, обновление токенов и валидацию пользователя.
    """

    def __init__(self, user_repo: UserRepository, session: AsyncSession, redis: Redis):
        self.user_repo = user_repo
        self.session = session
        self.redis = redis

    async def send_verification_code(self, email: str) -> dict:
        """
        Генерирует код, сохраняет в Redis и ставит задачу на отправку письма.
        """
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ResourceAlreadyExistsError("User with this email already exists")

        code = str(random.randint(100000, 999999))

        redis_key = f"verification_code:{email}"
        await self.redis.setex(redis_key, 300, code)

        subject = "Your Verification Code"
        body = f"Code: {code}"

        send_email_task.delay(email, subject, body)

        logger.info("Verification code sent to %s", email)
        return {"status": "sent", "message": "Verification code sent to email"}

    async def verify_email_code(
        self, email: str, code: str
    ) -> VerificationTokenResponse:
        """
        Проверяет код из Redis.
        """
        redis_key = f"verification_code:{email}"
        stored_code = await self.redis.get(redis_key)

        if not stored_code:
            raise AuthenticationFailedError("Verification code expired or invalid")

        if stored_code != code:
            raise AuthenticationFailedError("Invalid verification code")

        await self.redis.delete(redis_key)

        token = JWTHandler.create_token(
            data={"sub": email},
            token_type="verification_email",
            expires_delta=timedelta(minutes=15),
        )

        return VerificationTokenResponse(
            verification_token=token, message="Email verified successfully"
        )

    async def register_user(self, data: UserRegister) -> dict:
        """
        Регистрирует пользователя. Требует токен подтвержденного Email.
        """
        logger.info("Registering new user: %s", data.email)

        payload = JWTHandler.decode_token(data.verification_token)
        if not payload:
            raise AuthenticationFailedError("Invalid or expired verification token")

        if payload.get("type") != "verification_email":
            raise AuthenticationFailedError(INVALID_TOKEN_TYPE)

        verified_email = payload.get("sub")

        if verified_email != data.email:
            raise PermissionDeniedError("Email in token does not match provided email")

        if await self.user_repo.get_by_email(data.email):
            raise ResourceAlreadyExistsError("User with this email already exists")

        hashed_password = PasswordHandler.get_password_hash(data.password)

        new_user = await self.user_repo.create_user(
            data, hashed_password, role=UserRole.USER
        )
        await self.session.commit()

        return {
            "id": new_user.id,
            "email": new_user.email,
            "message": "User registered successfully",
        }

    async def request_password_reset(self, email: str) -> dict:
        """
        Сброс пароля через письмо.
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            return {
                "message": "If this email exists, a password reset link has been sent."
            }

        reset_token = JWTHandler.create_reset_password_token(email)
        reset_link = f"https://swipe.com/reset-password?token={reset_token}"

        subject = "Password Reset Request"
        body = f"Click the link to reset your password: {reset_link}\nValid for 30 minutes."

        send_email_task.delay(email, subject, body)

        logger.info("Password reset email queued for %s", email)
        return {"message": "If this email exists, a password reset link has been sent."}

    async def reset_password(self, data: ResetPasswordRequest) -> dict:
        """Сброс пароля пользователя при наличии валидного токена."""
        payload = JWTHandler.decode_token(data.token)
        if not payload or payload.get("type") != "reset_password":
            raise AuthenticationFailedError("Invalid token")

        email = payload.get("sub")
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ResourceNotFoundError(USER_NOT_FOUND)

        new_hash = PasswordHandler.get_password_hash(data.new_password)
        await self.user_repo.update_user(user, {"hashed_password": new_hash})
        await self.session.commit()
        return {"message": "Password reset"}

    async def authenticate_user(self, data: UserLogin) -> Token:
        """
        Проверяет email/пароль и выдает пару токенов (Access + Refresh).
        """
        logger.debug("Authenticating user: %s", data.email)

        user = await self.user_repo.get_by_email(data.email)
        if not user or not PasswordHandler.verify_password(
            data.password, user.hashed_password
        ):
            logger.warning("Authentication failed for user: %s", data.email)
            raise AuthenticationFailedError("Incorrect email or password")

        logger.info("User authenticated successfully: id=%s", user.id)
        return self._generate_tokens(user)

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Обновляет Access Token по валидному Refresh Token.
        """
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            logger.warning("Refresh token decode failed")
            raise AuthenticationFailedError("Invalid refresh token")

        if payload.get("type") != "refresh":
            logger.warning(
                "Invalid token type for refresh endpoint: %s", payload.get("type")
            )
            raise AuthenticationFailedError(INVALID_TOKEN_TYPE)

        user_id = int(payload.get("sub"))
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.warning("User not found during token refresh: id=%s", user_id)
            raise AuthenticationFailedError(USER_NOT_FOUND)

        logger.info("Token refreshed successfully for user: id=%s", user.id)
        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> Token:
        """Вспомогательный метод генерации пары"""
        payload = {"sub": str(user.id), "role": user.role.value}

        access_token = JWTHandler.create_access_token(payload)
        refresh_token = JWTHandler.create_refresh_token(payload)

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def get_current_user(self, token: str) -> User:
        """
        Валидирует Access Token и возвращает объект пользователя.
        Используется в зависимостях (Depends).
        """
        payload = JWTHandler.decode_token(token)
        if not payload:
            logger.warning("Token validation failed: Decode error")
            raise AuthenticationFailedError("Could not validate credentials")

        if payload.get("type") != "access":
            logger.warning(
                "Token validation failed: Wrong type (%s)", payload.get("type")
            )
            raise AuthenticationFailedError(INVALID_TOKEN_TYPE)

        user_id = int(payload.get("sub"))
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.warning("Token validation failed: User %s not found", user_id)
            raise AuthenticationFailedError(USER_NOT_FOUND)

        return user
