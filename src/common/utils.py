"""src/common/utils.py."""

import re
from typing import Optional

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


def extract_public_id_for_image(image_url: str) -> Optional[str]:
    """
    Извлекает public_id из ссылки Cloudinary (для картинок).
    Обрезает расширение в конце.
    Пример: https://res.cloudinary.com/.../swipe_project/real_estate/xyz.jpg
    -> swipe_project/real_estate/xyz
    """
    if not image_url:
        return None
    match = re.search(r"(swipe_project/.*)\.", image_url)
    if match:
        return match.group(1)
    return None
