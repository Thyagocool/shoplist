from uuid import UUID

import jwt

from config import settings
from src.infrastructure.auth.jwt_service import JWTService


class RefreshTokenUseCase:
    async def execute(self, refresh_token: str) -> str:
        try:
            payload = JWTService.decode_token(refresh_token)
        except jwt.PyJWTError:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = UUID(payload["sub"])
        return JWTService.create_access_token(user_id)
