import json
import os
from base64 import b64encode
from unittest.mock import patch

# Set test environment variables BEFORE any imports from the app
# This ensures Settings are initialized with test values and .env is not loaded
os.environ["APP_NAME"] = "test_app"
test_api_keys = {
    "test_admin_key": {"username": "test_admin", "roles": ["admin", "user"]},
    "test_user_key": {"username": "test_user", "roles": ["user"]},
}
os.environ["api_keys"] = b64encode(json.dumps(test_api_keys).encode()).decode()
os.environ["oauth_secret_key"] = "test_secret_key_at_least_32_characters_long"
os.environ["oauth_client_id"] = "test_client_id"
os.environ["oauth_client_secret"] = "test_client_secret"
os.environ["redis_host"] = "localhost"
os.environ["redis_port"] = "6379"

import pytest
from fakeredis import FakeServer, FakeStrictRedis
from fastapi.testclient import TestClient

from {{cookiecutter.project_name}}.main import app
from {{cookiecutter.project_name}}.settings import get_settings


@pytest.fixture
def fake_redis():
    """Provide a fake Redis instance for testing."""
    # Use FakeServer to avoid deprecation warnings
    server = FakeServer()
    fake = FakeStrictRedis(server=server)
    fake.ping()
    return fake


@pytest.fixture(autouse=True)
def mock_redis_connection(fake_redis):
    """Automatically mock Redis connection for all tests."""
    from {{cookiecutter.project_name}}.queue.connection import get_redis_connection

    # Clear the lru_cache before each test
    get_redis_connection.cache_clear()

    # Mock redis.Redis to return fake_redis
    with patch("redis.Redis", return_value=fake_redis):
        yield

    # Clear cache after test
    get_redis_connection.cache_clear()


@pytest.fixture
def client():
    """FastAPI test client with fake Redis."""
    # Clear the lru_cache before tests
    get_settings.cache_clear()

    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client

    # Clear after tests
    get_settings.cache_clear()


@pytest.fixture
def admin_headers():
    """Headers with admin API key."""
    return {"Authorization": "Bearer test_admin_key"}


@pytest.fixture
def user_headers():
    """Headers with user API key."""
    return {"Authorization": "Bearer test_user_key"}


@pytest.fixture
def invalid_headers():
    """Headers with invalid API key."""
    return {"Authorization": "Bearer invalid_key"}


@pytest.fixture
def sample_transform_data():
    """Sample data for transform_data task."""
    return {"name": "John", "age": 30, "city": "NYC", "country": None}


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for process_csv task."""
    return """name,age,score
Alice,25,95.5
Bob,30,87.2
Charlie,35,92.0"""
