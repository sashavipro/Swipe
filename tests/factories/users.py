"""tests/factories/users.py."""

from polyfactory.factories.pydantic_factory import ModelFactory
from src.apps.auth.schemas import UserRegister, UserCreateBase


class UserRegisterFactory(ModelFactory[UserRegister]):
    """
    Factory for creating UserRegister models for testing.
    """

    __model__ = UserRegister

    @classmethod
    def phone(cls) -> str:
        """Generates a random valid phone number."""
        return cls.__faker__.numerify("+###########")


class UserCreateFactory(ModelFactory[UserCreateBase]):
    """
    Factory for creating UserCreateBase models for testing.
    """

    __model__ = UserCreateBase

    @classmethod
    def phone(cls) -> str:
        """Generates a random valid phone number."""
        return cls.__faker__.numerify("+###########")
