"""src/tests/factories/announcement.py."""

from decimal import Decimal
from polyfactory.factories.pydantic_factory import ModelFactory
from src.schemas.real_estate import AnnouncementCreate
from src.models.real_estate import RoomCount, CommunicationMethod


class AnnouncementCreateFactory(ModelFactory[AnnouncementCreate]):
    """
    Factory for creating Announcement models for testing.
    """

    __model__ = AnnouncementCreate

    apartment_id = None

    number_of_rooms = RoomCount.ONE
    communication_method = CommunicationMethod.ANY

    images = ["R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"]

    @classmethod
    def price(cls) -> Decimal:
        """Generates a random price within Postgres Numeric limits."""
        return cls.__faker__.pydecimal(left_digits=8, right_digits=2, positive=True)

    @classmethod
    def area(cls) -> Decimal:
        """Generates a random area within Postgres Numeric limits."""
        return cls.__faker__.pydecimal(left_digits=3, right_digits=2, positive=True)

    @classmethod
    def kitchen_area(cls) -> Decimal:
        """Generates a random kitchen area within Postgres Numeric limits."""
        return cls.__faker__.pydecimal(left_digits=2, right_digits=2, positive=True)

    @classmethod
    def ceiling_height(cls) -> Decimal:
        """Generates a random ceiling height between 2 and 5 meters."""
        return cls.__faker__.pydecimal(
            left_digits=1, right_digits=2, positive=True, min_value=2, max_value=5
        )

    @classmethod
    def agent_commission(cls) -> Decimal:
        """Generates a random agent commission within Postgres Numeric limits."""
        return cls.__faker__.pydecimal(left_digits=4, right_digits=2, positive=True)
