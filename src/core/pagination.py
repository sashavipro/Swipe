"""src/core/pagination.py."""

from typing import Annotated
from fastapi import Query


class Pagination:
    """
    Common dependency for pagination parameters (limit/offset).
    """

    # pylint: disable=too-few-public-methods
    def __init__(
        self,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Number of records per page")
        ] = 20,
        offset: Annotated[
            int, Query(ge=0, description="Number of records to skip")
        ] = 0,
    ):
        self.limit = limit
        self.offset = offset
