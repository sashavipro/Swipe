"""src/common/utils.py."""

from src.models.users import User, UserRole
from src.common.exceptions import PermissionDeniedError


def check_owner_or_admin(user: User, owner_id: int, error_msg: str) -> None:
    """
    Проверяет, является ли пользователь владельцем ресурса или администратором/агентом.
    Если нет — вызывает исключение.
    """
    is_owner = user.id == owner_id
    is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

    if not is_owner and not is_admin:
        raise PermissionDeniedError(error_msg)
