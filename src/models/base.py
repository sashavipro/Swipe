import datetime
from typing import Annotated

from sqlalchemy import MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, declared_attr

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

int_pk = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[datetime.datetime, mapped_column(server_default=func.now())]

updated_at = Annotated[
    datetime.datetime, mapped_column(server_default=func.now(), onupdate=func.now())
]


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
