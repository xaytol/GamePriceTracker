from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_wishlist_service
from app.core.exceptions import (
    AccessDeniedError,
    GameNotFoundError,
    WishlistAlreadyExistsError,
    WishlistNotFoundError,
)
from app.database.models import UserModel
from app.schemas.wishlist import WishlistCreate, WishlistResponse, WishlistUpdate
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/wishlists", tags=["Wishlists"])


@router.post("/", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    data: WishlistCreate,
    current_user: UserModel = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Добавление игры в вишлист пользователя"""
    try:
        wishlist = await service.add_to_wishlist(user_id=current_user.id, data=data)
        return wishlist
    except GameNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except WishlistAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)


@router.get("/", response_model=list[WishlistResponse])
async def get_user_wishlists(
    current_user: UserModel = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Получение вишлистов пользователя"""
    return await service.get_user_wishlists(user_id=current_user.id)


@router.put("/{wishlist_id}", response_model=WishlistResponse)
async def update_wishlist(
    wishlist_id: int,
    data: WishlistUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Обновление целевой цены в вишлисте"""
    try:
        wishlist = await service.update_wishlist(
            wishlist_id=wishlist_id, user_id=current_user.id, data=data
        )
        return wishlist
    except WishlistNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=e.message)


@router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    wishlist_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Удаление игры из вишлиста"""
    try:
        await service.remove_from_wishlist(wishlist_id, user_id=current_user.id)
    except WishlistNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=e.message)
