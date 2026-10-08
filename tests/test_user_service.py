from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.database.models import UserModel
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def user_service(mock_session):
    service = UserService(mock_session)
    service.user_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_register_user_success(user_service, mock_session):
    user_service.user_repo.get_by_email.return_value = None
    created_user = UserModel(id=1, email="test@test.com", hashed_password="hashed")
    user_service.user_repo.create.return_value = created_user

    user_data = UserCreate(email="test@test.com", password="password123")
    result = await user_service.register_user(user_data)

    assert result.email == "test@test.com"
    user_service.user_repo.create.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(created_user)


@pytest.mark.asyncio
async def test_register_user_already_exists(user_service, mock_session):
    user_service.user_repo.get_by_email.return_value = UserModel(
        id=1, email="test@test.com", hashed_password="hashed"
    )
    user_data = UserCreate(email="test@test.com", password="password123")

    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(user_data)

    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_success(user_service, mock_session):
    user_service.user_repo.get_by_email.return_value = UserModel(
        id=1, email="test@test.com", hashed_password="hashed"
    )

    # Мокаем внутреннюю проверку пароля, чтобы не делать реальные вычисления bcrypt в юнит-тесте
    with patch.object(user_service, "_verify_password", return_value=True):
        result = await user_service.authenticate_user("test@test.com", "password123")
        assert result.email == "test@test.com"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(user_service, mock_session):
    user_service.user_repo.get_by_email.return_value = UserModel(
        id=1, email="test@test.com", hashed_password="hashed"
    )

    with patch.object(user_service, "_verify_password", return_value=False):
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user("test@test.com", "wrongpassword")
