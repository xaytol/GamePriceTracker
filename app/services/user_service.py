import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.database.models import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def register_user(self, user_data: UserCreate) -> UserModel:
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError("Пользователь с таким email уже существует")

        hashed_password = await asyncio.to_thread(self._hash_password, user_data.password)

        user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password
        )
        return await self.user_repo.create(user)

    async def authenticate_user(self, email: str, password: str) -> UserModel | None:
        user = await self.user_repo.get_by_email(email)
        # Защита от timing attack
        if user is None:
            dummy_hash = await asyncio.to_thread(self._hash_password, password)
            await asyncio.to_thread(self._verify_password, password, dummy_hash)
            raise InvalidCredentialsError("Неверный email или пароль")
        
        is_valid = await asyncio.to_thread(self._verify_password, password, user.hashed_password)
        if not is_valid:
            raise InvalidCredentialsError("Неверный email или пароль")
        
        return user       