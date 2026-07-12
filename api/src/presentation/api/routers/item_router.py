from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.item_dtos import (
    CreateItemInput,
    UpdateItemInput,
)
from src.application.use_cases.item.create_item import CreateItemUseCase
from src.application.use_cases.item.deactivate_item import DeactivateItemUseCase
from src.application.use_cases.item.list_items import ListItemsUseCase
from src.application.use_cases.item.update_item import UpdateItemUseCase
from src.infrastructure.database.repositories.item_repository import ItemRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.item_schemas import (
    CreateItemRequest,
    ItemResponse,
    UpdateItemRequest,
)
from src.infrastructure.database.config import get_session

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: CreateItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ItemResponse:
    repo = ItemRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CreateItemUseCase(repo, uow)

    result = await use_case.execute(
        CreateItemInput(
            name=body.name,
            category_id=body.category_id,
            user_id=user_id,
            default_unit=body.default_unit,
            default_quantity=body.default_quantity,
            min_stock=body.min_stock,
            max_stock=body.max_stock,
        )
    )

    return ItemResponse(
        id=result.id,
        name=result.name,
        category_id=result.category_id,
        category_name=result.category_name,
        default_unit=result.default_unit,
        default_quantity=float(result.default_quantity),
        min_stock=float(result.min_stock),
        max_stock=float(result.max_stock),
        active=result.active,
    )


@router.get("", response_model=list[ItemResponse])
async def list_items(
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[ItemResponse]:
    repo = ItemRepository(session)
    use_case = ListItemsUseCase(repo)

    items = await use_case.execute(user_id)

    return [
        ItemResponse(
            id=it.id,
            name=it.name,
            category_id=it.category_id,
            category_name=it.category_name,
            default_unit=it.default_unit,
            default_quantity=float(it.default_quantity),
            min_stock=float(it.min_stock),
            max_stock=float(it.max_stock),
            active=it.active,
        )
        for it in items
    ]


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    body: UpdateItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ItemResponse:
    repo = ItemRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = UpdateItemUseCase(repo, uow)

    result = await use_case.execute(
        item_id,
        user_id,
        UpdateItemInput(
            name=body.name,
            category_id=body.category_id,
            default_unit=body.default_unit,
            default_quantity=body.default_quantity,
            min_stock=body.min_stock,
            max_stock=body.max_stock,
        ),
    )

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(
        id=result.id,
        name=result.name,
        category_id=result.category_id,
        category_name=result.category_name,
        default_unit=result.default_unit,
        default_quantity=float(result.default_quantity),
        min_stock=float(result.min_stock),
        max_stock=float(result.max_stock),
        active=result.active,
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> None:
    repo = ItemRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = DeactivateItemUseCase(repo, uow)

    success = await use_case.execute(item_id, user_id)
    if not success:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Item not found")
