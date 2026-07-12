from uuid import UUID, uuid4

from config import settings
from src.application.dtos.auth_dtos import RegisterInput, TokenOutput, UserOutput
from src.domain.entities.user import User
from src.domain.interfaces.unit_of_work import UnitOfWork
from src.domain.value_objects.email import Email
from src.infrastructure.auth.jwt_service import JWTService
from src.infrastructure.auth.password_service import PasswordService
from src.infrastructure.database.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        uow: UnitOfWork,
    ) -> None:
        self.user_repo = user_repo
        self.uow = uow

    async def execute(self, input_data: RegisterInput) -> tuple[UserOutput, TokenOutput]:
        # Validate email
        email = Email(input_data.email)

        # Check if email already exists
        existing = await self.user_repo.find_by_email(email.value)
        if existing:
            raise ValueError("Email already registered")

        # Hash password
        password_hash = await PasswordService.hash_password(input_data.password)

        # Create user entity
        user = User.create(
            name=input_data.name,
            email=email,
            password_hash=password_hash,
        )

        # Map to model and save
        from src.infrastructure.database.models.user_model import UserModel

        user_model = UserModel(
            id=user.id,
            name=user.name,
            email=user.email.value,
            password_hash=user.password_hash,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        await self.user_repo.save(user_model)
        await self.uow.commit()

        # Generate tokens
        access_token = JWTService.create_access_token(user.id)
        refresh_token = JWTService.create_refresh_token(user.id)

        user_output = UserOutput(id=user.id, name=user.name, email=user.email.value)
        token_output = TokenOutput(access_token=access_token, refresh_token=refresh_token)

        return user_output, token_output
