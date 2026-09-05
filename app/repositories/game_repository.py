from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import GameModel
from app.repositories.base import BaseRepository

class GameRepository(BaseRepository[GameModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=GameModel)
