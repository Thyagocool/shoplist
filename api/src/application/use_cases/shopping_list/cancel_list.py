from uuid import UUID

from sqlalchemy import select

from src.application.dtos.shopping_list_dtos import ShoppingListOutput
from src.domain.entities.shopping_list import ShoppingListStatus
from src.infrastructure.database.models.store_model import StoreModel
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CancelShoppingListUseCase:
    def __init__(self, repo: ShoppingListRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def _get_store_name(self, store_id: UUID | None) -> str | None:
        if not store_id:
            return None
        result = await self.repo.session.execute(
            select(StoreModel.name).where(StoreModel.id == store_id)
        )
        return str(result.scalar_one_or_none()) if result.scalar_one_or_none() else None

    async def execute(self, list_id: UUID, user_id: UUID) -> ShoppingListOutput | None:
        model = await self.repo.find_by_id(list_id)
        if not model or str(model.user_id) != str(user_id):
            return None

        model.status = ShoppingListStatus.CANCELLED.value

        await self.repo.save(model)
        await self.uow.commit()

        store_name = await self._get_store_name(model.store_id)

        return ShoppingListOutput(
            id=model.id,
            name=model.name,
            status=model.status,
            store_id=model.store_id,
            store_name=store_name,
            completed_at=model.completed_at,
        )
