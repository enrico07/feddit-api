import contextlib
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the modules to test
from app.database.postgre import PostgreClient


@pytest.fixture
def postgres_client():
    """Fixture to create a test PostgreClient instance"""
    client = PostgreClient()
    return client


@pytest.mark.asyncio
async def test_connect_to_db(postgres_client, monkeypatch):
    """Test PostgreClient's connect_to_db method"""
    # Mock asyncpg.create_pool
    mock_pool = AsyncMock()

    async def mock_create_pool(*args, **kwargs):
        return mock_pool

    monkeypatch.setattr("asyncpg.create_pool", mock_create_pool)

    # Call the method
    await postgres_client.connect_to_db()

    # Assert the pool was set correctly
    assert postgres_client.pool == mock_pool


@pytest.mark.asyncio
async def test_get_subfeddit_id_success(postgres_client):
    """Test PostgreClient's get_subfeddit_id method for successful case"""
    # Create a mock connection
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1}

    # Create an actual async context manager class
    @contextlib.asynccontextmanager
    async def mock_acquire():
        yield mock_conn

    # Replace the pool's acquire method with our context manager
    postgres_client.pool = AsyncMock()
    postgres_client.pool.acquire = mock_acquire

    # Call the method
    result = await postgres_client.get_subfeddit_id("Dummy Topic 1")

    # Assertions
    mock_conn.fetchrow.assert_called_once_with(
        "SELECT id FROM subfeddit WHERE title = $1;", "Dummy Topic 1"
    )
    assert result == 1


@pytest.mark.asyncio
async def test_get_subfeddit_id_not_found(postgres_client):
    """Test PostgreClient's get_subfeddit_id method when subfeddit not found"""
    # Create a mock connection
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    # Create an actual async context manager class
    @contextlib.asynccontextmanager
    async def mock_acquire():
        yield mock_conn

    # Replace the pool's acquire method with our context manager
    postgres_client.pool = AsyncMock()
    postgres_client.pool.acquire = mock_acquire

    # Call the method and expect exception
    with pytest.raises(ValueError) as excinfo:
        await postgres_client.get_subfeddit_id("wrong_subfeddit")

    assert "not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_comments_no_filters(postgres_client):
    """Test PostgreClient's get_comments method without date filters"""
    # Create a mock connection
    mock_conn = AsyncMock()

    # Configure mock to return comments
    mock_comments = [
        {"id": 33730, "text": "Hate it! Hate it! Hate it! Hate it!"},
        {"id": 33729, "text": "Hate it! Hate it! Hate it! Nooooooo!"},
    ]
    mock_conn.fetch.return_value = mock_comments

    # Create an actual async context manager class
    @contextlib.asynccontextmanager
    async def mock_acquire():
        yield mock_conn

    # Replace the pool's acquire method with our context manager
    postgres_client.pool = AsyncMock()
    postgres_client.pool.acquire = mock_acquire

    # Call the method
    result = await postgres_client.get_comments(subfeddit_id=1, n_comments=2)

    # Assertions
    mock_conn.fetch.assert_called_once_with(
        "SELECT id, text FROM comment WHERE subfeddit_id = $1 ORDER BY created_at DESC LIMIT $2;",
        1,
        2,
    )
    assert result == mock_comments


@pytest.mark.asyncio
async def test_get_comments_with_date_filters(postgres_client):
    """Test PostgreClient's get_comments method with date filters"""
    # Create a mock connection
    mock_conn = AsyncMock()

    # Configure mock to return comments
    mock_comments = [{"id": 8759, "text": "Well done! Enjoy! Good work. Proud of you."}]
    mock_conn.fetch.return_value = mock_comments

    # Create an actual async context manager class
    @contextlib.asynccontextmanager
    async def mock_acquire():
        yield mock_conn

    # Replace the pool's acquire method with our context manager
    postgres_client.pool = AsyncMock()
    postgres_client.pool.acquire = mock_acquire

    # Call the method with date filters
    result = await postgres_client.get_comments(
        subfeddit_id=1, from_date="01-06-2022", to_date="05-06-2022", n_comments=1
    )

    # Calculate expected timestamp params
    from_timestamp = int(datetime.strptime("01-06-2022", "%d-%m-%Y").timestamp())
    to_timestamp = int(datetime.strptime("05-06-2022", "%d-%m-%Y").timestamp())

    # Assertions
    mock_conn.fetch.assert_called_once_with(
        "SELECT id, text FROM comment WHERE subfeddit_id = $1 AND created_at >= $2 AND created_at <= $3 ORDER BY created_at DESC LIMIT $4;",
        1,
        from_timestamp,
        to_timestamp,
        1,
    )
    assert result == mock_comments
