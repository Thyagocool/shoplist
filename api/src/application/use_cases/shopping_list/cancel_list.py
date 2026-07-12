from uuid import UUID

from src.application.dtos.shopping_list_dtos import ShoppingListOutput
from src.domain.entities.shopping_list import ShoppingListStatus
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CancelShoppingListUseCase:
    def __init__(self, repo: ShoppingListRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, list_id: UUID, user_id: UUID) -> ShoppingListOutput | None:
        model = await self.repo.find_by_id(list_id)
        if not model or str(model.user_id) != str(user_id):
            return None

        model.status = ShoppingListStatus.CANCELLED.value

        await self.repo.save(model)
        await self.uow.commit()

        return ShoppingListOutput(
            id=model.id,
            name=model.name,
            status=model.status,
            completed_at=model.completed_at,
        )
