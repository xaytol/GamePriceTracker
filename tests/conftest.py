import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Фикстура клиента для тестов"""
    return TestClient(app)
