from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.category_dtos import CreateCategoryInput, UpdateCategoryInput
from src.application.use_cases.category.create_category import CreateCategoryUseCase
from src.application.use_cases.category.delete_category import DeleteCategoryUseCase
from src.application.use_cases.category.list_categories import ListCategoriesUseCase
from src.application.use_cases.category.update_category import UpdateCategoryUseCase
from src.infrastructure.database.config import get_session
from src.infrastructure.database.repositories.category_repository import CategoryRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.category_schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreateRequest,
    user_id: object = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    repo = CategoryRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CreateCategoryUseCase(repo, uow)

    result = await use_case.execute(
        CreateCategoryInput(name=request.name, user_id=user_id)  # type: ignore[arg-type]
    )
    return CategoryResponse(id=str(result.id), name=result.name)


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    user_id: object = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    repo = CategoryRepository(session)
    use_case = ListCategoriesUseCase(repo)
    results = await use_case.execute(user_id)  # type: ignore[arg-type]
    return [CategoryResponse(id=str(c.id), name=c.name) for c in results]


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    request: CategoryUpdateRequest,
    user_id: object = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    repo = CategoryRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = UpdateCategoryUseCase(repo, uow)

    try:
        result = await use_case.execute(
            category_id, UpdateCategoryInput(name=request.name)
        )
        return CategoryResponse(id=str(result.id), name=result.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    user_id: object = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    repo = CategoryRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = DeleteCategoryUseCase(repo, uow)

    try:
        await use_case.execute(category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
