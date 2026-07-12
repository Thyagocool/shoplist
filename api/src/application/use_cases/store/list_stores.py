from uuid import UUID

from src.application.dtos.store_dtos import StoreOutput
from src.infrastructure.database.repositories.store_repository import StoreRepository


class ListStoresUseCase:
    def __init__(self, repo: StoreRepository) -> None:
        self.repo = repo

    async def execute(self, user_id: UUID) -> list[StoreOutput]:
        models = await self.repo.find_by_user_id(user_id)
        return [StoreOutput(id=m.id, name=m.name) for m in models]
