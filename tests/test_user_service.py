from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.database.models import UserModel
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def user_service(mock_session):
    service = UserService(mock_session)
    service.user_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_register_user_success(user_service):
    user_service.user_repo.get_by_email.return_value = None
    user_service.user_repo.create.return_value = UserModel(
        id=1, email="test@test.com", hashed_password="hashed"
    )

    user_data = UserCreate(email="test@test.com", password="password123")
    result = await user_service.register_user(user_data)

    assert result.email == "test@test.com"
    user_service.user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_already_exists(user_service):
    user_service.user_repo.get_by_email.return_value = UserModel(
        id=1, email="test@test.com", hashed_password="hashed"
    )

    user_data = UserCreate(email="test@test.com", password="password123")

    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(user_data)


@pytest.mark.asyncio
async def test_authenticate_user_success(user_service):
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("password123")

    user_service.user_repo.get_by_email.return_value = UserModel(
        id=1, email="test@test.com", hashed_password=hashed
    )

    result = await user_service.authenticate_user("test@test.com", "password123")
    assert result.email == "test@test.com"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(user_service):
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("password123")

    user_service.user_repo.get_by_email.return_value = UserModel(
        id=1, email="test@test.com", hashed_password=hashed
    )

    with pytest.raises(InvalidCredentialsError):
        await user_service.authenticate_user("test@test.com", "wrongpassword")
