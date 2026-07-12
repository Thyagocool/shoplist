from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.store_dtos import CreateStoreInput, UpdateStoreInput
from src.application.use_cases.store.create_store import CreateStoreUseCase
from src.application.use_cases.store.delete_store import DeleteStoreUseCase
from src.application.use_cases.store.list_stores import ListStoresUseCase
from src.application.use_cases.store.update_store import UpdateStoreUseCase
from src.infrastructure.database.config import get_session
from src.infrastructure.database.repositories.store_repository import StoreRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.store_schemas import (
    CreateStoreRequest,
    StoreResponse,
    UpdateStoreRequest,
)

router = APIRouter(prefix="/api/v1/stores", tags=["stores"])


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    body: CreateStoreRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> StoreResponse:
    repo = StoreRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CreateStoreUseCase(repo, uow)

    result = await use_case.execute(
        CreateStoreInput(name=body.name, user_id=user_id)
    )

    return StoreResponse(id=result.id, name=result.name)


@router.get("", response_model=list[StoreResponse])
async def list_stores(
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[StoreResponse]:
    repo = StoreRepository(session)
    use_case = ListStoresUseCase(repo)

    stores = await use_case.execute(user_id)
    return [StoreResponse(id=s.id, name=s.name) for s in stores]


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: UUID,
    body: UpdateStoreRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> StoreResponse:
    repo = StoreRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = UpdateStoreUseCase(repo, uow)

    result = await use_case.execute(
        store_id, user_id, UpdateStoreInput(name=body.name)
    )

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Store not found")

    return StoreResponse(id=result.id, name=result.name)


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    store_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> None:
    repo = StoreRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = DeleteStoreUseCase(repo, uow)

    success = await use_case.execute(store_id, user_id)
    if not success:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Store not found")
