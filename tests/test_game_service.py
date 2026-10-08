from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import GameAlreadyExistsError, GameNotFoundError
from app.database.models import GameModel
from app.schemas.game import GameCreate, GameUpdate
from app.services.game_service import GameService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def game_service(mock_session):
    service = GameService(mock_session)
    service.game_repo = AsyncMock()
    service.price_history_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_create_game_success(game_service, mock_session):
    game_service.game_repo.get_by_external_id.return_value = None
    created_game = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )
    game_service.game_repo.create.return_value = created_game

    # Явно передаем image_url=None, чтобы Pydantic/MyPy не ругались
    game_data = GameCreate(
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url=None,
    )
    result = await game_service.create_game(game_data)

    assert result.title == "Test Game"
    game_service.game_repo.create.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(created_game)


@pytest.mark.asyncio
async def test_create_game_already_exists(game_service, mock_session):
    game_service.game_repo.get_by_external_id.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url=None,
    )

    game_data = GameCreate(
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url=None,
    )

    with pytest.raises(GameAlreadyExistsError):
        await game_service.create_game(game_data)

    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_game_success(game_service, mock_session):
    game_service.game_repo.get_by_id.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url=None,
    )
    result = await game_service.get_game(1)
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_game_not_found(game_service, mock_session):
    game_service.game_repo.get_by_id.return_value = None
    with pytest.raises(GameNotFoundError):
        await game_service.get_game(999)


@pytest.mark.asyncio
async def test_update_game_success(game_service, mock_session):
    game_id = 1
    # Явно передаем все поля, даже если они None
    update_data = GameUpdate(title=None, current_price=Decimal("29.99"), image_url=None)
    mock_game = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url=None,
    )

    game_service.game_repo.get_by_id.return_value = mock_game
    game_service.game_repo.update.return_value = mock_game

    result = await game_service.update_game(game_id, update_data)

    game_service.game_repo.update.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_game)
    assert result.current_price == Decimal("29.99")


@pytest.mark.asyncio
async def test_delete_game_success(game_service, mock_session):
    game_id = 1
    mock_game = GameModel(
        id=1, title="Test", external_id="1", current_price=Decimal("10"), image_url=None
    )
    game_service.game_repo.get_by_id.return_value = mock_game
    game_service.game_repo.delete = AsyncMock()

    await game_service.delete_game(game_id)

    game_service.game_repo.delete.assert_called_once_with(mock_game)
    mock_session.commit.assert_called_once()
