from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.checkout_dtos import CheckoutInput, CheckoutItemInput
from src.application.dtos.shopping_list_dtos import (
    AddListItemInput,
    CreateShoppingListInput,
)
from src.application.use_cases.shopping_list.add_list_item import AddListItemUseCase
from src.application.use_cases.shopping_list.cancel_list import CancelShoppingListUseCase
from src.application.use_cases.shopping_list.checkout_list import CheckoutListUseCase
from src.application.use_cases.shopping_list.complete_list import CompleteShoppingListUseCase
from src.application.use_cases.shopping_list.create_list import CreateShoppingListUseCase
from src.application.use_cases.shopping_list.get_list import GetShoppingListUseCase
from src.application.use_cases.shopping_list.list_lists import ListShoppingListsUseCase
from src.application.use_cases.shopping_list.remove_list_item import RemoveListItemUseCase
from src.application.use_cases.shopping_list.toggle_item import ToggleListItemUseCase
from src.application.use_cases.shopping_list.update_list_item import UpdateListItemUseCase
from src.infrastructure.database.config import get_session
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.repositories.movement_repository import MovementRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.api.middleware.auth_middleware import get_current_user_id
from src.presentation.schemas.checkout_schemas import CheckoutRequest, CheckoutResponse, MovementResponse
from src.presentation.schemas.shopping_list_schemas import (
    AddListItemRequest,
    CreateShoppingListRequest,
    ListItemResponse,
    ShoppingListResponse,
    UpdateListItemRequest,
)

router = APIRouter(prefix="/api/v1/lists", tags=["shopping lists"])


@router.post("", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    body: CreateShoppingListRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ShoppingListResponse:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CreateShoppingListUseCase(repo, uow)

    result = await use_case.execute(
        CreateShoppingListInput(
            name=body.name,
            store_id=body.store_id,
            user_id=user_id,
        )
    )

    return ShoppingListResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        store_id=result.store_id,
        store_name=result.store_name,
        completed_at=result.completed_at,
    )


@router.post("/{list_id}/checkout", response_model=CheckoutResponse)
async def checkout_list(
    list_id: UUID,
    body: CheckoutRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> CheckoutResponse:
    list_repo = ShoppingListRepository(session)
    movement_repo = MovementRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CheckoutListUseCase(list_repo, movement_repo, uow)

    try:
        result = await use_case.execute(
            CheckoutInput(
                shopping_list_id=list_id,
                user_id=user_id,
                items=[
                    CheckoutItemInput(
                        shopping_list_item_id=item.shopping_list_item_id,
                        price_cents=item.price_cents,
                        store_id=item.store_id,
                    )
                    for item in body.items
                ],
            )
        )
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))

    return CheckoutResponse(
        movements=[
            MovementResponse(
                id=m.id,
                sequential_code=m.sequential_code,
                item_name=m.item_name,
                quantity=m.quantity,
                unit=m.unit,
                price_cents=m.price_cents,
                store_name=m.store_name,
            )
            for m in result.movements
        ],
        list_status=result.list_status,
    )


@router.get("", response_model=list[ShoppingListResponse])
async def list_lists(
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> list[ShoppingListResponse]:
    repo = ShoppingListRepository(session)
    use_case = ListShoppingListsUseCase(repo)

    lists = await use_case.execute(user_id)
    return [
        ShoppingListResponse(
            id=l.id,
            name=l.name,
            status=l.status,
            store_id=l.store_id,
            store_name=l.store_name,
            completed_at=l.completed_at,
            items=[
                ListItemResponse(
                    id=i.id,
                    pre_registered_item_id=i.pre_registered_item_id,
                    custom_name=i.custom_name,
                    item_name=i.item_name,
                    estimated_quantity=i.estimated_quantity,
                    unit=i.unit,
                    checked=i.checked,
                    price_cents=i.price_cents,
                )
                for i in l.items
            ],
        )
        for l in lists
    ]


@router.get("/{list_id}", response_model=ShoppingListResponse)
async def get_list(
    list_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ShoppingListResponse:
    repo = ShoppingListRepository(session)
    use_case = GetShoppingListUseCase(repo)

    result = await use_case.execute(list_id, user_id)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ShoppingListResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        store_id=result.store_id,
        store_name=result.store_name,
        completed_at=result.completed_at,
        items=[
            ListItemResponse(
                id=i.id,
                pre_registered_item_id=i.pre_registered_item_id,
                custom_name=i.custom_name,
                estimated_quantity=i.estimated_quantity,
                unit=i.unit,
                checked=i.checked,
                price_cents=i.price_cents,
                item_name=i.item_name,
            )
            for i in result.items
        ],
    )


@router.post("/{list_id}/items", response_model=ListItemResponse, status_code=status.HTTP_201_CREATED)
async def add_list_item(
    list_id: UUID,
    body: AddListItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ListItemResponse:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = AddListItemUseCase(repo, uow)

    try:
        result = await use_case.execute(
            AddListItemInput(
                shopping_list_id=list_id,
                user_id=user_id,
                pre_registered_item_id=body.pre_registered_item_id,
                custom_name=body.custom_name,
                estimated_quantity=body.estimated_quantity,
                unit=body.unit,
                store_id=body.store_id,
            )
        )
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))

    return ListItemResponse(
        id=result.id,
        pre_registered_item_id=result.pre_registered_item_id,
        custom_name=result.custom_name,
        estimated_quantity=result.estimated_quantity,
        unit=result.unit,
        checked=result.checked,
        price_cents=result.price_cents,
        item_name=result.item_name,
    )


@router.patch("/items/{item_id}/toggle", response_model=ListItemResponse)
async def toggle_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ListItemResponse:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = ToggleListItemUseCase(repo, uow)

    try:
        result = await use_case.execute(item_id, user_id)
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Item not found")

    return ListItemResponse(
        id=result.id,
        pre_registered_item_id=result.pre_registered_item_id,
        custom_name=result.custom_name,
        estimated_quantity=result.estimated_quantity,
        unit=result.unit,
        checked=result.checked,
        price_cents=result.price_cents,
        item_name=result.item_name,
    )


@router.patch("/items/{item_id}", response_model=ListItemResponse)
async def update_list_item(
    item_id: UUID,
    body: UpdateListItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ListItemResponse:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = UpdateListItemUseCase(repo, uow)

    try:
        result = await use_case.execute(
            item_id=item_id,
            user_id=user_id,
            unit=body.unit,
            estimated_quantity=body.estimated_quantity,
            price_cents=body.price_cents,
        )
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Item not found")

    return ListItemResponse(
        id=result.id,
        pre_registered_item_id=result.pre_registered_item_id,
        custom_name=result.custom_name,
        item_name=result.item_name,
        estimated_quantity=result.estimated_quantity,
        unit=result.unit,
        checked=result.checked,
        price_cents=result.price_cents,
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_list_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> None:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = RemoveListItemUseCase(repo, uow)

    success = await use_case.execute(item_id, user_id)
    if not success:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/{list_id}/complete", response_model=ShoppingListResponse)
async def complete_list(
    list_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ShoppingListResponse:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CompleteShoppingListUseCase(repo, uow)

    result = await use_case.execute(list_id, user_id)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ShoppingListResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        store_id=result.store_id,
        store_name=result.store_name,
        completed_at=result.completed_at,
    )


@router.post("/{list_id}/cancel", response_model=ShoppingListResponse)
async def cancel_list(
    list_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session=Depends(get_session),
) -> ShoppingListResponse:
    repo = ShoppingListRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CancelShoppingListUseCase(repo, uow)

    result = await use_case.execute(list_id, user_id)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Shopping list not found")

    return ShoppingListResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        store_id=result.store_id,
        store_name=result.store_name,
        completed_at=result.completed_at,
    )
