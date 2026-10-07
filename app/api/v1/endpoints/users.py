from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_user_service
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, service: UserService = Depends(get_user_service)
):
    """Регистрация нового пользователя"""
    try:
        user = await service.register_user(user_data)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)


@router.post("/login", response_model=UserResponse)
async def login_user(
    login_data: UserLogin, service: UserService = Depends(get_user_service)
):
    """Вход в систему (пока без JWT, просто проверка)"""
    try:
        user = await service.authenticate_user(login_data.email, login_data.password)
        return user
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=e.message)
