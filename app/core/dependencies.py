from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.services.game_service import GameService
from app.services.user_service import UserService
from app.services.wishlist_service import WishlistService


# пагинация
class Pagination:
    def __init__(
        self,
        limit: int = Query(100, ge=1, le=1000, description="сколько записей вернуть"),
        offset: int = Query(0, ge=0, description="сколько записей пропустить"),
    ):
        self.limit = limit
        self.offset = offset


# фабрики сервисов
async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(session)


async def get_game_service(
    session: AsyncSession = Depends(get_async_session),
) -> GameService:
    return GameService(session)


async def get_wishlist_service(
    session: AsyncSession = Depends(get_async_session),
) -> WishlistService:
    return WishlistService(session)
