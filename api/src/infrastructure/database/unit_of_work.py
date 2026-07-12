from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.unit_of_work import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of the Unit of Work pattern."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        return self

    async def __aexit__(self, *args: object) -> None:
        exc_type = args[0]
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
