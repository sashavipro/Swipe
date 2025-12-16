"""src/services/auth.py."""

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import UserRepository
from src.schemas.auth import UserRegister, UserLogin, Token
from src.infrastructure.security.password import PasswordHandler
from src.infrastructure.security.jwt import JWTHandler
from src.models.users import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    """
    Сервис аутентификации и авторизации.
    Отвечает за регистрацию, вход, обновление токенов и валидацию пользователя.
    """

    def __init__(self, user_repo: UserRepository, session: AsyncSession):
        self.user_repo = user_repo
        self.session = session

    async def register_user(self, data: UserRegister) -> dict:
        """
        Регистрирует нового пользователя с ролью USER.
        """
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

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

    async def authenticate_user(self, data: UserLogin) -> Token:
        """
        Проверяет email/пароль и выдает пару токенов (Access + Refresh).
        """
        user = await self.user_repo.get_by_email(data.email)
        if not user or not PasswordHandler.verify_password(
            data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self._generate_tokens(user)

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Обновляет Access Token по валидному Refresh Token.
        """
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = int(payload.get("sub"))

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return self._generate_tokens(user)

    def _generate_tokens(self, user) -> Token:
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(payload.get("sub"))

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
