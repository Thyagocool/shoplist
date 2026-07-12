from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dtos import LoginInput, RegisterInput
from src.application.use_cases.auth.login_user import LoginUserUseCase
from src.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from src.application.use_cases.auth.register_user import RegisterUserUseCase
from src.infrastructure.database.config import get_session
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.auth_schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    user_repo = UserRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = RegisterUserUseCase(user_repo, uow)

    try:
        user_output, token_output = await use_case.execute(
            RegisterInput(
                name=request.name,
                email=request.email,
                password=request.password,
            )
        )
        return {
            "user": UserResponse(
                id=str(user_output.id),
                name=user_output.name,
                email=user_output.email,
            ),
            "tokens": TokenResponse(
                access_token=token_output.access_token,
                refresh_token=token_output.refresh_token,
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login")
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    user_repo = UserRepository(session)
    use_case = LoginUserUseCase(user_repo)

    try:
        user_output, token_output = await use_case.execute(
            LoginInput(email=request.email, password=request.password)
        )
        return {
            "user": UserResponse(
                id=str(user_output.id),
                name=user_output.name,
                email=user_output.email,
            ),
            "tokens": TokenResponse(
                access_token=token_output.access_token,
                refresh_token=token_output.refresh_token,
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh")
async def refresh(request: RefreshRequest) -> dict:
    use_case = RefreshTokenUseCase()
    try:
        access_token = await use_case.execute(request.refresh_token)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def me(
    user_id: object = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session)
    user = await user_repo.find_by_id(user_id)  # type: ignore[arg-type]
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
    )
