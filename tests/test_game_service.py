from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import GameAlreadyExistsError, GameNotFoundError
from app.database.models import GameModel
from app.schemas.game import GameCreate
from app.services.game_service import GameService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def game_service(mock_session):
    service = GameService(mock_session)
    service.game_repo = AsyncMock()
    service.price_history_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_create_game_success(game_service):
    game_service.game_repo.get_by_external_id.return_value = None
    game_service.game_repo.create.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )

    game_data = GameCreate(
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )
    result = await game_service.create_game(game_data)

    assert result.title == "Test Game"
    game_service.game_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_game_already_exists(game_service):
    game_service.game_repo.get_by_external_id.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )

    game_data = GameCreate(
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )

    with pytest.raises(GameAlreadyExistsError):
        await game_service.create_game(game_data)


@pytest.mark.asyncio
async def test_get_game_success(game_service):
    game_service.game_repo.get_by_id.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )

    result = await game_service.get_game(1)
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_game_not_found(game_service):
    game_service.game_repo.get_by_id.return_value = None

    with pytest.raises(GameNotFoundError):
        await game_service.get_game(999)
