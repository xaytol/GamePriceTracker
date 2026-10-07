from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserModel
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=UserModel)

    async def get_by_email(self, email: str) -> UserModel | None:
        """Поиск пользователя по email (для логина/регистрации)"""
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()
