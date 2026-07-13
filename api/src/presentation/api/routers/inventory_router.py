from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.inventory_dtos import DeclareInventoryInput
from src.application.use_cases.inventory.declare_inventory import DeclareInventoryUseCase
from src.application.use_cases.inventory.list_inventory import ListInventoryUseCase
from src.infrastructure.database.config import get_session
from src.infrastructure.database.repositories.inventory_repository import InventoryRepository
from src.infrastructure.database.repositories.item_repository import ItemRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.inventory_schemas import (
    DeclareInventoryRequest,
    InventoryResponseOld as InventoryResponse,
)

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def declare_inventory(
    body: DeclareInventoryRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> InventoryResponse:
    inventory_repo = InventoryRepository(session)
    item_repo = ItemRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = DeclareInventoryUseCase(inventory_repo, item_repo, uow)

    result = await use_case.execute(
        DeclareInventoryInput(
            shopping_list_id=body.shopping_list_id,
            pre_registered_item_id=body.pre_registered_item_id,
            declared_quantity=body.declared_quantity,
            user_id=user_id,
        )
    )

    return InventoryResponse(
        id=result.id,
        shopping_list_id=result.shopping_list_id,
        pre_registered_item_id=result.pre_registered_item_id,
        item_name=result.item_name,
        declared_quantity=result.declared_quantity,
        calculated_need=result.calculated_need,
    )


@router.get("", response_model=list[InventoryResponse])
async def list_inventory(
    list_id: UUID = Query(..., alias="list_id"),
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[InventoryResponse]:
    repo = InventoryRepository(session)
    use_case = ListInventoryUseCase(repo)

    declarations = await use_case.execute(list_id, user_id)

    return [
        InventoryResponse(
            id=d.id,
            shopping_list_id=d.shopping_list_id,
            pre_registered_item_id=d.pre_registered_item_id,
            item_name=d.item_name,
            declared_quantity=d.declared_quantity,
            calculated_need=d.calculated_need,
        )
        for d in declarations
    ]
