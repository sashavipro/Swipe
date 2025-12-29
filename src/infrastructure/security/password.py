"""src/infrastructure/security/password.py."""

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class PasswordHandler:
    """
    Handler for working with passwords (hashing and verification).
    Uses pwdlib (Argon2 by default).
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Checks if the password matches the hash."""
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generates password hash."""
        return password_hash.hash(password)
