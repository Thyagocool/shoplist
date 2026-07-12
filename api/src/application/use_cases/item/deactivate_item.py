from uuid import UUID

from src.infrastructure.database.repositories.item_repository import ItemRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class DeactivateItemUseCase:
    def __init__(self, repo: ItemRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, item_id: UUID, user_id: UUID) -> bool:
        model = await self.repo.find_by_id(item_id)
        if not model or str(model.user_id) != str(user_id):
            return False

        model.active = False
        await self.repo.save(model)
        await self.uow.commit()
        return True
