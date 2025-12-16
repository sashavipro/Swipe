"""src/infrastructure/security/password.py."""

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class PasswordHandler:
    """
    Хендлер для работы с паролями (хеширование и верификация).
    Использует pwdlib (Argon2 по умолчанию).
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет совпадение пароля и хеша."""
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Генерирует хеш пароля."""
        return password_hash.hash(password)
