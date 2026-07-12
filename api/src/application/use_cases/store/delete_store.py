from uuid import UUID

from src.infrastructure.database.repositories.store_repository import StoreRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class DeleteStoreUseCase:
    def __init__(self, repo: StoreRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, store_id: UUID, user_id: UUID) -> bool:
        model = await self.repo.find_by_id(store_id)
        if not model or str(model.user_id) != str(user_id):
            return False

        await self.repo.delete(store_id)
        await self.uow.commit()
        return True
