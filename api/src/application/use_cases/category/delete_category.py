from uuid import UUID

from src.infrastructure.database.repositories.category_repository import CategoryRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class DeleteCategoryUseCase:
    def __init__(self, repo: CategoryRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, category_id: UUID) -> None:
        model = await self.repo.find_by_id(category_id)
        if not model:
            raise ValueError("Category not found")

        # Check if category has items
        item_count = await self.repo.count_items(category_id)
        if item_count > 0:
            raise ValueError("Cannot delete category with linked items")

        await self.repo.delete(category_id)
        await self.uow.commit()
