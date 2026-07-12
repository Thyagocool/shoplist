import bcrypt

from src.domain.interfaces.auth_service import AuthService


class PasswordService:
    """Password hashing and verification using bcrypt."""

    @staticmethod
    async def hash_password(password: str) -> str:
        """Hash a password with bcrypt (cost factor = 12)."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    async def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
