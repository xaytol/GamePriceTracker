from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import (
    AccessDeniedError,
    GameNotFoundError,
)
from app.database.models import GameModel, WishlistModel
from app.schemas.wishlist import WishlistCreate, WishlistUpdate
from app.services.wishlist_service import WishlistService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def wishlist_service(mock_session):
    service = WishlistService(mock_session)
    service.wishlist_repo = AsyncMock()
    service.game_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_add_to_wishlist_success(wishlist_service, mock_session):
    user_id = 11
    data = WishlistCreate(game_id=1, target_price=Decimal("1500.00"))

    wishlist_service.game_repo.get_by_id.return_value = MagicMock(spec=GameModel)
    wishlist_service.wishlist_repo.get_by_user_and_game.return_value = None

    created_wishlist = WishlistModel(
        id=1, user_id=user_id, game_id=1, target_price=Decimal("1500.00")
    )
    wishlist_service.wishlist_repo.create.return_value = created_wishlist

    result = await wishlist_service.add_to_wishlist(user_id, data)

    wishlist_service.wishlist_repo.create.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(created_wishlist)
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_add_to_wishlist_game_not_found(wishlist_service, mock_session):
    user_id = 11
    data = WishlistCreate(game_id=999, target_price=Decimal("1500.00"))
    wishlist_service.game_repo.get_by_id.return_value = None

    with pytest.raises(GameNotFoundError):
        await wishlist_service.add_to_wishlist(user_id, data)

    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_wishlist_success(wishlist_service, mock_session):
    wishlist_id = 1
    user_id = 11
    data = WishlistUpdate(target_price=Decimal("2000.00"))

    mock_wishlist = MagicMock(spec=WishlistModel)
    mock_wishlist.user_id = user_id
    mock_wishlist.target_price = Decimal("1500.00")

    wishlist_service.wishlist_repo.get_by_id.return_value = mock_wishlist
    wishlist_service.wishlist_repo.update.return_value = mock_wishlist

    result = await wishlist_service.update_wishlist(wishlist_id, user_id, data)

    wishlist_service.wishlist_repo.update.assert_called_once_with(mock_wishlist)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_wishlist)
    assert result.target_price == Decimal("2000.00")


@pytest.mark.asyncio
async def test_update_wishlist_access_denied(wishlist_service, mock_session):
    wishlist_id = 1
    user_id = 11
    data = WishlistUpdate(target_price=Decimal("2000.00"))

    mock_wishlist = MagicMock(spec=WishlistModel)
    mock_wishlist.user_id = 99  # Чужой вишлист

    wishlist_service.wishlist_repo.get_by_id.return_value = mock_wishlist

    with pytest.raises(AccessDeniedError):
        await wishlist_service.update_wishlist(wishlist_id, user_id, data)

    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_remove_from_wishlist_success(wishlist_service, mock_session):
    wishlist_id = 1
    user_id = 11

    mock_wishlist = MagicMock(spec=WishlistModel)
    mock_wishlist.user_id = user_id

    wishlist_service.wishlist_repo.get_by_id.return_value = mock_wishlist
    wishlist_service.wishlist_repo.delete = AsyncMock()

    await wishlist_service.remove_from_wishlist(wishlist_id, user_id)

    wishlist_service.wishlist_repo.delete.assert_called_once_with(mock_wishlist)
    mock_session.commit.assert_called_once()
