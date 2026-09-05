from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import WishlistModel
from app.repositories.base import BaseRepository

class WishlistRepository(BaseRepository[WishlistModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=WishlistModel)
