from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    AccessDeniedError,
    GameNotFoundError,
    WishlistAlreadyExistsError,
)
from app.database.models import GameModel, WishlistModel
from app.schemas.wishlist import WishlistCreate, WishlistUpdate
from app.services.wishlist_service import WishlistService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def wishlist_service(mock_session):
    service = WishlistService(mock_session)
    service.wishlist_repo = AsyncMock()
    service.game_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_add_to_wishlist_success(wishlist_service):
    wishlist_service.game_repo.get_by_id.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )
    wishlist_service.wishlist_repo.get_by_user_and_game.return_value = None
    wishlist_service.wishlist_repo.create.return_value = WishlistModel(
        id=1, user_id=1, game_id=1, target_price=Decimal("15.00")
    )

    data = WishlistCreate(game_id=1, target_price=Decimal("15.00"))
    result = await wishlist_service.add_to_wishlist(user_id=1, data=data)

    assert result.user_id == 1


@pytest.mark.asyncio
async def test_add_to_wishlist_game_not_found(wishlist_service):
    wishlist_service.game_repo.get_by_id.return_value = None

    data = WishlistCreate(game_id=999, target_price=Decimal("15.00"))

    with pytest.raises(GameNotFoundError):
        await wishlist_service.add_to_wishlist(user_id=1, data=data)


@pytest.mark.asyncio
async def test_add_to_wishlist_already_exists(wishlist_service):
    wishlist_service.game_repo.get_by_id.return_value = GameModel(
        id=1,
        title="Test Game",
        external_id="steam_123",
        current_price=Decimal("19.99"),
        image_url="http://example.com/image.jpg",
    )
    wishlist_service.wishlist_repo.get_by_user_and_game.return_value = WishlistModel(
        id=1, user_id=1, game_id=1, target_price=Decimal("15.00")
    )

    data = WishlistCreate(game_id=1, target_price=Decimal("15.00"))

    with pytest.raises(WishlistAlreadyExistsError):
        await wishlist_service.add_to_wishlist(user_id=1, data=data)


@pytest.mark.asyncio
async def test_update_wishlist_access_denied(wishlist_service):
    wishlist_service.wishlist_repo.get_by_id.return_value = WishlistModel(
        id=1, user_id=2, game_id=1, target_price=Decimal("15.00")
    )

    data = WishlistUpdate(target_price=Decimal("10.00"))

    with pytest.raises(AccessDeniedError):
        await wishlist_service.update_wishlist(wishlist_id=1, user_id=1, data=data)
