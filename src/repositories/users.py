"""src/repositories/users.py."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User, UserRole, AgentContact
from src.schemas.users import UserCreateBase, AgentContactSchema


class UserRepository:
    """
    Репозиторий для работы с пользователями.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Ищет пользователя по email."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Ищет пользователя по ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self, data: UserCreateBase, hashed_password: str, role: UserRole = UserRole.USER
    ) -> User:
        """Создает нового пользователя в базе данных."""
        user = User(
            email=data.email,
            hashed_password=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: User, update_data: dict) -> User:
        """Обновляет поля пользователя"""
        for key, value in update_data.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_agent_contact(self, user: User, data: AgentContactSchema):
        """
        Создает или обновляет контакты агента для пользователя.
        """
        if user.agent_contact:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user.agent_contact, key, value)
        else:
            new_contact = AgentContact(
                user_id=user.id, **data.model_dump(exclude_unset=True)
            )
            self.session.add(new_contact)
            user.agent_contact = new_contact
        await self.session.flush()
