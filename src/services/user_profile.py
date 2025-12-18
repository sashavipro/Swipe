"""src/services/user_profile.py."""

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import UserRepository
from src.infrastructure.storage import ImageStorage
from src.infrastructure.security.password import PasswordHandler
from src.schemas.users import UserUpdate, EmployeeCreate, UserResponse


class UserProfileService:
    """
    Сервис для работы с пользователями.
    """

    def __init__(
        self, repo: UserRepository, session: AsyncSession, storage: ImageStorage
    ):
        self.repo = repo
        self.session = session
        self.storage = storage

    async def create_employee(self, data: EmployeeCreate) -> UserResponse:
        """
        Создает пользователя с указанной ролью.
        """
        if await self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        hashed_password = PasswordHandler.get_password_hash(data.password)
        user = await self.repo.create_user(data, hashed_password, role=data.role)
        await self.session.commit()
        return user

    async def update_my_profile(self, user_id: int, data: UserUpdate) -> UserResponse:
        """
        Обновляет профиль пользователя: личные данные, настройки и контакты агента.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = data.model_dump(exclude_unset=True)
        agent_data = user_data.pop("agent_contact", None)

        if "email" in user_data:
            existing = await self.repo.get_by_email(user_data["email"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Email already taken")

        if user_data:
            await self.repo.update_user(user, user_data)
        if agent_data is not None:
            await self.repo.update_agent_contact(user, data.agent_contact)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_avatar(self, user_id: int, file: UploadFile) -> UserResponse:
        """Загрузка и обновление аватарки"""
        user = await self.repo.get_by_id(user_id)
        image_url = await self.storage.upload_file(file.file, folder="avatars")
        updated_user = await self.repo.update_user(user, {"avatar": image_url})
        await self.session.commit()
        return updated_user
