from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import PriceHistoryModel
from app.repositories.base import BaseRepository
from decimal import Decimal

class PriceHistoryRepository(BaseRepository[PriceHistoryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=PriceHistoryModel)

    async def get_by_game_id(self, game_id: int) -> list[PriceHistoryModel]:
        """Получить всю историю цен для конкретной игры"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.game_id == game_id)
            .order_by(self.model.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def add_record(self, game_id: int, price: Decimal) -> PriceHistoryModel:
        """Добавить запись в историю цен"""
        history = PriceHistoryModel(game_id=game_id, price=price)
        return await self.create(history)