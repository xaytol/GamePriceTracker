from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import GameModel
from app.repositories.base import BaseRepository


class GameRepository(BaseRepository[GameModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=GameModel)

    async def get_by_external_id(self, external_id: str) -> GameModel | None:
        """Ищет игру по её внешнему ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, game_id: int) -> GameModel | None:
        """Блокирует строку для обновления"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.id == game_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()