from uuid import UUID

from src.application.dtos.category_dtos import CategoryOutput, UpdateCategoryInput
from src.infrastructure.database.repositories.category_repository import CategoryRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class UpdateCategoryUseCase:
    def __init__(self, repo: CategoryRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, category_id: UUID, input_data: UpdateCategoryInput) -> CategoryOutput:
        model = await self.repo.find_by_id(category_id)
        if not model:
            raise ValueError("Category not found")

        model.name = input_data.name
        await self.repo.save(model)
        await self.uow.commit()

        return CategoryOutput(id=model.id, name=model.name)
