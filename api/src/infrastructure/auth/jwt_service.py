from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from config import settings


class JWTService:
    """JWT token creation and validation."""

    @staticmethod
    def create_access_token(user_id: UUID) -> str:
        """Create a short-lived access token."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    @staticmethod
    def create_refresh_token(user_id: UUID) -> str:
        """Create a longer-lived refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a JWT token. Raises jwt.PyJWTError on failure."""
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
