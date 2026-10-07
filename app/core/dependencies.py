from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database.models import UserModel
from app.database.session import get_async_session
from app.services.game_service import GameService
from app.services.user_service import UserService
from app.services.wishlist_service import WishlistService

# Схема для получения токена из заголовка Authorization: Bearer <token>
# Указываем путь к эндпоинту логина для автоматической генерации кнопки в Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")


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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> UserModel:
    """
    Зависимость для получения текущего авторизованного пользователя из JWT токена.
    """
    # расшифровываем токен
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # достаем user_id (мы сохранили его под ключом "sub" при создании токена)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит идентификатор пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ищем пользователя в БД
    user_service = UserService(session)
    user = await user_service.user_repo.get_by_id(int(user_id_str))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
