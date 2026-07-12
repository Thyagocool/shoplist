from src.application.dtos.auth_dtos import LoginInput, TokenOutput, UserOutput
from src.infrastructure.auth.jwt_service import JWTService
from src.infrastructure.auth.password_service import PasswordService
from src.infrastructure.database.repositories.user_repository import UserRepository


class LoginUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, input_data: LoginInput) -> tuple[UserOutput, TokenOutput]:
        # Find user by email
        user_model = await self.user_repo.find_by_email(input_data.email)
        if not user_model:
            raise ValueError("Invalid email or password")

        # Verify password
        valid = await PasswordService.verify_password(
            input_data.password, user_model.password_hash
        )
        if not valid:
            raise ValueError("Invalid email or password")

        # Generate tokens
        access_token = JWTService.create_access_token(user_model.id)
        refresh_token = JWTService.create_refresh_token(user_model.id)

        user_output = UserOutput(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
        )
        token_output = TokenOutput(access_token=access_token, refresh_token=refresh_token)

        return user_output, token_output
