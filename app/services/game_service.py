from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.database.models import GameModel, PriceHistoryModel
from app.repositories.game_repository import GameRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.schemas.game import GameCreate, GameUpdate
from app.core.exceptions import GameNotFoundError, GameAlreadyExistsError


class GameService:
    def __init__(self, session: AsyncSession):
        self.game_repo = GameRepository(session)
        self.price_history_repo = PriceHistoryRepository(session)

    async def create_game(self, game_data: GameCreate) -> GameModel:
        """Создание новой игры"""
        existing = await self.game_repo.get_by_external_id(game_data.external_id)
        if existing:
            raise GameAlreadyExistsError("Игра с таким external_id уже существует")
        
        # маппинг Pydantic -> ORM
        game_model = GameModel(**game_data.model_dump())
        
        return await self.game_repo.create(game_model)

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
            
        return await self.game_repo.update(game)

    async def delete_game(self, game_id: int) -> None:
        """Удаление игры"""
        game = await self.get_game(game_id)
        await self.game_repo.delete(game)

    async def get_price_history(self, game_id: int) -> list[PriceHistoryModel]:
        """Получение истории цен для игры (связка двух репозиториев)"""
        # сначала проверяем, что игра вообще существует
        await self.get_game(game_id) 
        
        # если ок, идем во второй репозиторий
        return await self.price_history_repo.get_by_game_id(game_id)
    
    async def update_game_price(self, game_id: int, new_price: Decimal) -> GameModel:
        """Обновление цены игры и запись в историю (для Celery-воркера)"""
        game = await self.get_game(game_id)
        
        # оптимизация: если цена не изменилась, не делаем лишних запросов в бд
        if game.current_price == new_price:
            return game

        # обновляем текущую цену в таблице games
        game.current_price = new_price
        await self.game_repo.update(game)

        # записываем изменение в историю цен
        await self.price_history_repo.add_record(game_id, new_price)

        # здесь будет логика проверки вишлистов:
        # если new_price <= target_price у кого-то из юзеров -> отправляем уведомление

        return game