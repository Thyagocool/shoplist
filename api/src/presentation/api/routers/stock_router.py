from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.use_cases.stock.list_stock import ListStockUseCase
from src.application.use_cases.stock.update_stock import (
    BatchUpdateStockUseCase,
    UpdateStockUseCase,
)
from src.infrastructure.database.config import get_session
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.stock_schemas import (
    BatchUpdateStockRequest,
    StockResponse,
    UpdateStockRequest,
    UpdateStockResponse,
)

router = APIRouter(prefix="/api/v1/stock", tags=["stock"])


@router.get("", response_model=list[StockResponse])
async def list_stock(
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[StockResponse]:
    use_case = ListStockUseCase(session)
    result = await use_case.execute(user_id)
    return [
        StockResponse(
            pre_registered_item_id=r.pre_registered_item_id,
            item_name=r.item_name,
            category_name=r.category_name,
            current_quantity=float(r.current_quantity),
            default_unit=r.default_unit,
            min_stock=float(r.min_stock),
            max_stock=float(r.max_stock),
        )
        for r in result
    ]


@router.put("/{item_id}", response_model=UpdateStockResponse)
async def update_stock(
    item_id: UUID,
    body: UpdateStockRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> UpdateStockResponse:
    use_case = UpdateStockUseCase(session)
    from src.application.dtos.stock_dtos import UpdateStockInput

    result = await use_case.execute(
        UpdateStockInput(
            pre_registered_item_id=item_id,
            current_quantity=body.current_quantity,
            user_id=user_id,
        )
    )
    return UpdateStockResponse(
        pre_registered_item_id=result.pre_registered_item_id,
        current_quantity=float(result.current_quantity),
    )


@router.put("", response_model=list[UpdateStockResponse])
async def batch_update_stock(
    body: BatchUpdateStockRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[UpdateStockResponse]:
    use_case = BatchUpdateStockUseCase(session)
    from src.application.dtos.stock_dtos import UpdateStockInput

    items = [
        UpdateStockInput(
            pre_registered_item_id=item.pre_registered_item_id,
            current_quantity=item.current_quantity,
            user_id=user_id,
        )
        for item in body.items
    ]
    results = await use_case.execute(items)
    return [
        UpdateStockResponse(
            pre_registered_item_id=r.pre_registered_item_id,
            current_quantity=float(r.current_quantity),
        )
        for r in results
    ]
