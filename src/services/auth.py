"""src/services/auth.py."""

import json
import logging
import random

from redis.asyncio import Redis
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import (
    ResourceAlreadyExistsError,
    AuthenticationFailedError,
    ResourceNotFoundError,
)
from src.repositories.users import UserRepository
from src.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    ResetPasswordRequest,
)
from src.infrastructure.security.password import PasswordHandler
from src.infrastructure.security.jwt import JWTHandler
from src.models.users import User, UserRole
from src.tasks.email import send_email_task

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    """
    Authentication and Authorization Service.
    Responsible for registration, login, token refresh, and user validation.
    """

    def __init__(self, user_repo: UserRepository, session: AsyncSession, redis: Redis):
        self.user_repo = user_repo
        self.session = session
        self.redis = redis

    async def register_user(self, data: UserRegister) -> dict:
        """
        Step 1: Initiate registration.
        Validates data, checks duplicates, saves temp data to Redis, sends email code.
        """
        logger.info("Initiating registration for: %s", data.email)

        if await self.user_repo.get_by_email(data.email):
            raise ResourceAlreadyExistsError()

        code = str(random.randint(100000, 999999))

        hashed_password = PasswordHandler.get_password_hash(data.password)

        registration_data = {
            "email": data.email,
            "password": hashed_password,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "phone": data.phone,
            "code": code,
        }

        redis_key = f"registration:{data.email}"
        await self.redis.setex(redis_key, 900, json.dumps(registration_data))

        subject = "Complete your registration"
        body = f"Your verification code is: {code}\nIt expires in 15 minutes."
        send_email_task.delay(data.email, subject, body)

        return {
            "status": "pending_verification",
            "message": "Verification code sent to email",
        }

    async def verify_registration(self, email: str, code: str) -> dict:
        """
        Step 2: Finalize registration.
        Checks code from Redis and creates user in Postgres.
        """
        logger.info("Verifying registration for: %s", email)

        redis_key = f"registration:{email}"
        raw_data = await self.redis.get(redis_key)

        if not raw_data:
            raise AuthenticationFailedError()

        data = json.loads(raw_data)

        if data["code"] != code:
            raise AuthenticationFailedError()

        user_create_data = UserRegister(
            email=data["email"],
            password="hashed_already",
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
        )

        try:
            new_user = await self.user_repo.create_user(
                data=user_create_data,
                hashed_password=data["password"],
                role=UserRole.USER,
            )
            await self.session.commit()
        except Exception as e:
            logger.error("DB Error during final registration: %s", e)
            raise ResourceAlreadyExistsError() from e

        await self.redis.delete(redis_key)

        return {
            "id": new_user.id,
            "email": new_user.email,
            "message": "User registered successfully",
        }

    async def request_password_reset(self, email: str) -> dict:
        """
        Password reset via email.
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
        """Reset user password given a valid token."""
        payload = JWTHandler.decode_token(data.token)
        if not payload or payload.get("type") != "reset_password":
            raise AuthenticationFailedError()

        email = payload.get("sub")
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ResourceNotFoundError()

        new_hash = PasswordHandler.get_password_hash(data.new_password)
        await self.user_repo.update_user(user, {"hashed_password": new_hash})
        await self.session.commit()
        return {"message": "Password reset"}

    async def authenticate_user(self, data: UserLogin) -> Token:
        """
        Checks email/password and issues a pair of tokens (Access + Refresh).
        """
        logger.debug("Authenticating user: %s", data.email)

        user = await self.user_repo.get_by_email(data.email)
        if not user or not PasswordHandler.verify_password(
            data.password, user.hashed_password
        ):
            logger.warning("Authentication failed for user: %s", data.email)
            raise AuthenticationFailedError()

        logger.info("User authenticated successfully: id=%s", user.id)
        return self._generate_tokens(user)

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refreshes Access Token using a valid Refresh Token.
        """
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            logger.warning("Refresh token decode failed")
            raise AuthenticationFailedError()

        if payload.get("type") != "refresh":
            logger.warning(
                "Invalid token type for refresh endpoint: %s", payload.get("type")
            )
            raise AuthenticationFailedError()

        user_id = int(payload.get("sub"))
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.warning("User not found during token refresh: id=%s", user_id)
            raise AuthenticationFailedError()

        logger.info("Token refreshed successfully for user: id=%s", user.id)
        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> Token:
        """Helper method to generate token pair."""
        payload = {"sub": str(user.id), "role": user.role.value}

        access_token = JWTHandler.create_access_token(payload)
        refresh_token = JWTHandler.create_refresh_token(payload)

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def get_current_user(self, token: str) -> User:
        """
        Validates Access Token and returns user object.
        Used in dependencies (Depends).
        """
        payload = JWTHandler.decode_token(token)
        if not payload:
            logger.warning("Token validation failed: Decode error")
            raise AuthenticationFailedError()

        if payload.get("type") != "access":
            logger.warning(
                "Token validation failed: Wrong type (%s)", payload.get("type")
            )
            raise AuthenticationFailedError()

        user_id = int(payload.get("sub"))
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.warning("Token validation failed: User %s not found", user_id)
            raise AuthenticationFailedError()

        return user
