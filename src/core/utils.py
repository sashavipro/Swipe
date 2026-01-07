"""src/core/utils.py."""

import re
from typing import Optional
from src.apps.users.models import User, UserRole
from src.core.exceptions import PermissionDeniedError


def check_owner_or_admin(user: User, owner_id: int, error_msg: str) -> None:
    """
    Checks if the user is the resource owner or an administrator/agent.
    If not, raises an exception.
    """
    is_owner = user.id == owner_id
    is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

    if not is_owner and not is_admin:
        raise PermissionDeniedError(error_msg)


def extract_public_id_for_image(image_url: str) -> Optional[str]:
    """
    Extracts public_id from a Cloudinary link (for images).
    Trims the extension at the end.
    Example: https://res.cloudinary.com/.../swipe_project/real_estate/xyz.jpg
    -> swipe_project/real_estate/xyz
    """
    if not image_url:
        return None
    match = re.search(r"(swipe_project/.*)\.", image_url)
    if match:
        return match.group(1)
    return None
