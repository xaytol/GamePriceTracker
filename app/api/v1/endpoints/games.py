from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.game import GameCreate, GameUpdate, GameResponse
from app.schemas.price_history import PriceHistoryResponse
from app.services.game_service import GameService
from app.core.dependencies import get_game_service, Pagination
from app.core.exceptions import GameNotFoundError, GameAlreadyExistsError

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    service: GameService = Depends(get_game_service)
):
    """Создание новой игры"""
    try:
        game = await service.create_game(game_data)
        return game
    except GameAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)


@router.get("/", response_model=list[GameResponse])
async def get_games(
    pagination: Pagination = Depends(),
    service: GameService = Depends(get_game_service)
):
    """Получение списка игр с пагинацией"""
    games = await service.get_games(pagination.limit, pagination.offset)
    return games


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    service: GameService = Depends(get_game_service)
):
    """Получение игры по ID"""
    try:
        game = await service.get_game(game_id)
        return game
    except GameNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.put("/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: int,
    game_data: GameUpdate,
    service: GameService = Depends(get_game_service)
):
    """Обновление игры"""
    try:
        game = await service.update_game(game_id, game_data)
        return game
    except GameNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    service: GameService = Depends(get_game_service)
):
    """Удаление игры"""
    try:
        await service.delete_game(game_id)
    except GameNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/{game_id}/price-history", response_model=list[PriceHistoryResponse])
async def get_price_history(
    game_id: int,
    service: GameService = Depends(get_game_service)
):
    """Получение истории цен для игры"""
    try:
        history = await service.get_price_history(game_id)
        return history
    except GameNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)