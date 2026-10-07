from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AccessDeniedError,
    GameNotFoundError,
    WishlistAlreadyExistsError,
    WishlistNotFoundError,
)
from app.database.models import WishlistModel
from app.repositories.game_repository import GameRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.wishlist import WishlistCreate, WishlistUpdate


class WishlistService:
    def __init__(self, session: AsyncSession):
        self.wishlist_repo = WishlistRepository(session)
        self.game_repo = GameRepository(session)

    async def add_to_wishlist(
        self, user_id: int, data: WishlistCreate
    ) -> WishlistModel:
        """Добавление игры в вишлист"""
        # проверяем, существует ли игра
        game = await self.game_repo.get_by_id(data.game_id)
        if not game:
            raise GameNotFoundError("Игра не найдена")

        # проверяем, не добавил ли юзер эту игру раньше
        existing = await self.wishlist_repo.get_by_user_and_game(user_id, data.game_id)
        if existing:
            raise WishlistAlreadyExistsError("Эта игра уже есть в вашем вишлисте")

        # создаем запись
        wishlist = WishlistModel(
            user_id=user_id, game_id=data.game_id, target_price=data.target_price
        )
        return await self.wishlist_repo.create(wishlist)

    async def get_user_wishlists(self, user_id: int) -> list[WishlistModel]:
        """Получение всех игр из вишлиста конкретного пользователя"""
        return await self.wishlist_repo.get_by_user_id(user_id)

    async def update_wishlist(
        self, wishlist_id: int, user_id: int, data: WishlistUpdate
    ) -> WishlistModel:
        """Обновление целевой цены в вишлисте"""
        # ищем запись
        wishlist = await self.wishlist_repo.get_by_id(wishlist_id)
        if not wishlist:
            raise WishlistNotFoundError("Запись в вишлисте не найдена")

        # права
        if wishlist.user_id != user_id:
            raise AccessDeniedError("Вы не можете изменять чужой вишлист")

        # обновляем данные
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(wishlist, field, value)

        return await self.wishlist_repo.update(wishlist)

    async def remove_from_wishlist(self, wishlist_id: int, user_id: int) -> None:
        """Удаление игры из вишлиста"""
        wishlist = await self.wishlist_repo.get_by_id(wishlist_id)
        if not wishlist:
            raise WishlistNotFoundError("Запись в вишлисте не найдена")

        # снова проверяем права перед удалением
        if wishlist.user_id != user_id:
            raise AccessDeniedError("Вы не можете удалять чужой вишлист")

        await self.wishlist_repo.delete(wishlist)
