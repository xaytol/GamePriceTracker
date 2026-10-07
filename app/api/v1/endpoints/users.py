from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_user_service
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.security import create_access_token
from app.database.models import UserModel
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
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


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin, service: UserService = Depends(get_user_service)
):
    """Вход в систему и получение JWT токена"""
    try:
        user = await service.authenticate_user(login_data.email, login_data.password)

        access_token = create_access_token(data={"sub": str(user.id)})

        return {"access_token": access_token, "token_type": "bearer"}

    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=e.message)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    """Получение данных текущего авторизованного пользователя"""
    return current_user
