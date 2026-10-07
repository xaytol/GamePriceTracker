from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import WishlistModel
from app.repositories.base import BaseRepository


class WishlistRepository(BaseRepository[WishlistModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=WishlistModel)

    async def get_by_user_and_game(
        self, user_id: int, game_id: int
    ) -> WishlistModel | None:
        """Проверяет, есть ли уже эта игра в вишлисте у конкретного пользователя"""
        result = await self.session.execute(
            select(self.model).where(
                (self.model.user_id == user_id) & (self.model.game_id == game_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[WishlistModel]:
        """Возвращает все записи вишлиста для конкретного пользователя"""
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return list(result.scalars().all())
