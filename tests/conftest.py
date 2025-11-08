import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.config import Settings
from src.core.mcp import ModelContextProtocol

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def mcp():
    return ModelContextProtocol()
