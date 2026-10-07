import asyncio

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.database.models import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session  # Сохраняем ссылку на сессию для commit
        self.user_repo = UserRepository(session)

    def _hash_password(self, password: str) -> str:
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)

    async def register_user(self, user_data: UserCreate) -> UserModel:
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError("Пользователь с таким email уже существует")

        hashed_password = await asyncio.to_thread(
            self._hash_password, user_data.password
        )

        user = UserModel(email=user_data.email, hashed_password=hashed_password)
        created_user = await self.user_repo.create(user)

        await self.session.commit()
        await self.session.refresh(created_user)

        return created_user

    async def authenticate_user(self, email: str, password: str) -> UserModel:
        user = await self.user_repo.get_by_email(email)

        if user is None:
            dummy_hash = await asyncio.to_thread(self._hash_password, password)
            await asyncio.to_thread(self._verify_password, password, dummy_hash)
            raise InvalidCredentialsError("Неверный email или пароль")

        is_valid = await asyncio.to_thread(
            self._verify_password, password, user.hashed_password
        )

        if not is_valid:
            raise InvalidCredentialsError("Неверный email или пароль")

        return user
