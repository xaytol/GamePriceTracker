from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import GameAlreadyExistsError, GameNotFoundError
from app.database.models import GameModel, PriceHistoryModel
from app.repositories.game_repository import GameRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.schemas.game import GameCreate, GameUpdate


class GameService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.game_repo = GameRepository(session)
        self.price_history_repo = PriceHistoryRepository(session)

    async def create_game(self, game_data: GameCreate) -> GameModel:
        """Создание новой игры"""
        existing = await self.game_repo.get_by_external_id(game_data.external_id)
        if existing:
            raise GameAlreadyExistsError("Игра с таким external_id уже существует")

        game_model = GameModel(**game_data.model_dump())
        created_game = await self.game_repo.create(game_model)

        await self.session.commit()
        await self.session.refresh(created_game)

        return created_game

    async def get_game(self, game_id: int) -> GameModel:
        """Получение игры по ID"""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            raise GameNotFoundError(f"Игра с id {game_id} не найдена")
        return game

    async def get_games(self, limit: int = 100, offset: int = 0) -> list[GameModel]:
        """Получение списка игр с пагинацией"""
        return await self.game_repo.get_paginated(limit, offset)

    async def update_game(self, game_id: int, game_data: GameUpdate) -> GameModel:
        """Обновление игры"""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            raise GameNotFoundError(f"Игра с id {game_id} не найдена")

        update_data = game_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(game, field, value)

        updated_game = await self.game_repo.update(game)

        await self.session.commit()
        await self.session.refresh(updated_game)

        return updated_game

    async def delete_game(self, game_id: int) -> None:
        """Удаление игры"""
        game = await self.get_game(game_id)
        await self.game_repo.delete(game)

        await self.session.commit()

    async def get_price_history(self, game_id: int) -> list[PriceHistoryModel]:
        """Получение истории цен для игры"""
        await self.get_game(game_id)
        return await self.price_history_repo.get_by_game_id(game_id)

    async def update_game_price(self, game_id: int, new_price: Decimal) -> GameModel:
        """Обновление цены игры и запись в историю (для Celery-воркера)"""
        game = await self.get_game(game_id)

        if game.current_price == new_price:
            return game

        game.current_price = new_price
        await self.game_repo.update(game)
        await self.price_history_repo.add_record(game_id, new_price)

        await self.session.commit()
        await self.session.refresh(game)

        return game
