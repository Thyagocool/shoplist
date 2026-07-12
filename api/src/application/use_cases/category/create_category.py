from uuid import UUID

from src.application.dtos.category_dtos import CategoryOutput, CreateCategoryInput
from src.domain.entities.category import Category
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.repositories.category_repository import CategoryRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CreateCategoryUseCase:
    def __init__(self, repo: CategoryRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, input_data: CreateCategoryInput) -> CategoryOutput:
        # Create entity
        category = Category.create(name=input_data.name, user_id=input_data.user_id)

        # Persist
        model = CategoryModel(id=category.id, name=category.name, user_id=category.user_id)
        await self.repo.save(model)
        await self.uow.commit()

        return CategoryOutput(id=category.id, name=category.name)
