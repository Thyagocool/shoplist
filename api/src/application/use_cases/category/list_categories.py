from uuid import UUID

from src.application.dtos.category_dtos import CategoryOutput
from src.infrastructure.database.repositories.category_repository import CategoryRepository


class ListCategoriesUseCase:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo

    async def execute(self, user_id: UUID) -> list[CategoryOutput]:
        models = await self.repo.find_by_user_id(user_id)
        return [CategoryOutput(id=m.id, name=m.name) for m in models]
