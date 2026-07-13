from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.inventory_dtos import CreateInventoryInput, InventoryItemInput
from src.application.use_cases.inventories.cancel_inventory import CancelInventoryUseCase
from src.application.use_cases.inventories.complete_inventory import CompleteInventoryUseCase
from src.application.use_cases.inventories.create_inventory import CreateInventoryUseCase
from src.application.use_cases.inventories.get_inventory import GetInventoryUseCase
from src.application.use_cases.inventories.list_inventories import ListInventoriesUseCase
from src.application.use_cases.inventories.remove_inventory_item import RemoveInventoryItemUseCase
from src.application.use_cases.inventories.update_inventory_items import UpdateInventoryItemsUseCase
from src.infrastructure.database.config import get_session
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.inventory_schemas import (
    CreateInventoryRequest,
    InventoryDetailResponse,
    InventoryItemResponse,
    InventorySummaryResponse,
    UpdateInventoryItemsRequest,
)

router = APIRouter(prefix="/api/v1/inventories", tags=["inventories"])


@router.get("", response_model=list[InventorySummaryResponse])
async def list_inventories(
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[InventorySummaryResponse]:
    use_case = ListInventoriesUseCase(session)
    result = await use_case.execute(user_id)
    return [
        InventorySummaryResponse(
            id=r.id,
            date=r.date,
            status=r.status,
            notes=r.notes,
            item_count=r.item_count,
            created_at=r.created_at,
        )
        for r in result
    ]


@router.post("", response_model=InventoryDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    body: CreateInventoryRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> InventoryDetailResponse:
    use_case = CreateInventoryUseCase(session)
    result = await use_case.execute(
        CreateInventoryInput(
            date=body.date or date.today(),
            notes=body.notes,
            items=[
                InventoryItemInput(
                    pre_registered_item_id=i.pre_registered_item_id,
                    declared_quantity=i.declared_quantity,
                )
                for i in body.items
            ],
            user_id=user_id,
        )
    )
    return InventoryDetailResponse(
        id=result.id,
        date=result.date,
        status=result.status,
        notes=result.notes,
        items=[
            InventoryItemResponse(
                id=i.id,
                pre_registered_item_id=i.pre_registered_item_id,
                item_name=i.item_name,
                category_name=i.category_name,
                declared_quantity=i.declared_quantity,
                previous_quantity=i.previous_quantity,
                default_unit=i.default_unit,
            )
            for i in result.items
        ],
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/{inventory_id}", response_model=InventoryDetailResponse)
async def get_inventory(
    inventory_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> InventoryDetailResponse:
    use_case = GetInventoryUseCase(session)
    result = await use_case.execute(inventory_id, user_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")

    return InventoryDetailResponse(
        id=result.id,
        date=result.date,
        status=result.status,
        notes=result.notes,
        items=[
            InventoryItemResponse(
                id=i.id,
                pre_registered_item_id=i.pre_registered_item_id,
                item_name=i.item_name,
                category_name=i.category_name,
                declared_quantity=i.declared_quantity,
                previous_quantity=i.previous_quantity,
                default_unit=i.default_unit,
            )
            for i in result.items
        ],
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.put("/{inventory_id}/items", response_model=InventoryDetailResponse)
async def update_inventory_items(
    inventory_id: UUID,
    body: UpdateInventoryItemsRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> InventoryDetailResponse:
    use_case = UpdateInventoryItemsUseCase(session)
    result = await use_case.execute(
        inventory_id,
        [
            InventoryItemInput(
                pre_registered_item_id=i.pre_registered_item_id,
                declared_quantity=i.declared_quantity,
            )
            for i in body.items
        ],
        user_id,
    )
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")

    return InventoryDetailResponse(
        id=result.id,
        date=result.date,
        status=result.status,
        notes=result.notes,
        items=[
            InventoryItemResponse(
                id=i.id,
                pre_registered_item_id=i.pre_registered_item_id,
                item_name=i.item_name,
                category_name=i.category_name,
                declared_quantity=i.declared_quantity,
                previous_quantity=i.previous_quantity,
                default_unit=i.default_unit,
            )
            for i in result.items
        ],
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.delete("/{inventory_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_inventory_item(
    inventory_id: UUID,
    item_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> None:
    use_case = RemoveInventoryItemUseCase(session)
    await use_case.execute(inventory_id, item_id, user_id)


@router.post("/{inventory_id}/complete", status_code=status.HTTP_200_OK)
async def complete_inventory(
    inventory_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> dict:
    use_case = CompleteInventoryUseCase(session)
    await use_case.execute(inventory_id, user_id)
    return {"status": "completed"}


@router.post("/{inventory_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_inventory(
    inventory_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> dict:
    use_case = CancelInventoryUseCase(session)
    await use_case.execute(inventory_id, user_id)
    return {"status": "cancelled"}
