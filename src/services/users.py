"""src/services/users.py."""

from datetime import timedelta, date
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import UserRepository
from src.schemas.users import (
    UserUpdate,
    EmployeeCreate,
    UserResponse,
    SubscriptionResponse,
)
from src.infrastructure.security.password import PasswordHandler
from src.infrastructure.storage import ImageStorage
from src.models.users import Subscription


class UserService:
    """
    Сервис для управления пользователями.
    Обрабатывает создание сотрудников, обновление профиля, аватарки и подписок.
    """

    def __init__(
        self, repo: UserRepository, session: AsyncSession, image_storage: ImageStorage
    ):
        self.repo = repo
        self.session = session
        self.storage = image_storage

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

    async def toggle_auto_renewal(self, user_id: int) -> SubscriptionResponse:
        """Вкл/Выкл автопродления"""
        user = await self.repo.get_by_id_with_subscription(user_id)
        if not user.subscription:
            raise HTTPException(status_code=400, detail="No active subscription")

        user.subscription.auto_renewal = not user.subscription.auto_renewal
        self.session.add(user.subscription)
        await self.session.commit()

        return user.subscription

    async def extend_subscription(
        self, user_id: int, days: int = 30
    ) -> SubscriptionResponse:
        """Продление подписки (Имитация оплаты)"""
        user = await self.repo.get_by_id_with_subscription(user_id)

        if user.subscription:
            # продлеваем от текущей даты окончания или от сегодня
            start_date = max(user.subscription.paid_to, date.today())
            user.subscription.paid_to = start_date + timedelta(days=days)
        else:
            new_sub = Subscription(
                user_id=user_id,
                paid_to=date.today() + timedelta(days=days),
                auto_renewal=True,
            )
            self.session.add(new_sub)
            user.subscription = new_sub

        await self.session.commit()
        await self.session.refresh(user, ["subscription"])
        return user.subscription
