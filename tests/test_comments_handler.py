import os
import sys
from unittest.mock import AsyncMock

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the modules to test
from app.handlers.comments_handler import CommentsHandler


@pytest.fixture
def comments_handler():
    """Fixture to create a test CommentsHandler instance"""
    handler = CommentsHandler()
    # Replace the real PostgreClient with a mock
    handler.db_client = AsyncMock()
    return handler


def test_get_polarity_positive():
    """Test CommentsHandler's get_polarity method for positive text"""
    polarity, classification = CommentsHandler.get_polarity(
        "This is amazing! I love it."
    )
    assert polarity > 0.1
    assert classification == "positive"


def test_get_polarity_negative():
    """Test CommentsHandler's get_polarity method for negative text"""
    polarity, classification = CommentsHandler.get_polarity(
        "This is terrible! I hate it."
    )
    assert polarity < -0.1
    assert classification == "negative"


def test_get_polarity_neutral():
    """Test CommentsHandler's get_polarity method for neutral text"""
    polarity, classification = CommentsHandler.get_polarity(
        "This is a neutral statement."
    )
    assert -0.1 <= polarity <= 0.1
    assert classification == "neutral"


@pytest.mark.asyncio
async def test_get_comments_basic(comments_handler):
    """Test CommentsHandler's get_comments method with basic parameters"""
    # Configure mocks
    comments_handler.db_client.get_subfeddit_id.return_value = 123
    comments_handler.db_client.get_comments.return_value = [
        {"id": 1, "text": "Positive comment!"},
        {"id": 2, "text": "Negative comment :("},
    ]

    # Call the method
    result = await comments_handler.get_comments(subfeddit_name="test_subfeddit")

    # Assertions
    comments_handler.db_client.get_subfeddit_id.assert_called_once_with(
        subfeddit_name="test_subfeddit"
    )
    comments_handler.db_client.get_comments.assert_called_once_with(
        subfeddit_id=123, from_date=None, to_date=None, n_comments=25
    )

    assert len(result) == 2
    assert "polarity_score" in result[0]
    assert "polarity_classification" in result[0]


@pytest.mark.asyncio
async def test_get_comments_with_polarity_filter(comments_handler):
    """Test CommentsHandler's get_comments method with polarity filtering"""
    # Configure mocks
    comments_handler.db_client.get_subfeddit_id.return_value = 123
    comments_handler.db_client.get_comments.return_value = [
        {"id": 1, "text": "Extremely positive comment!!!!"},
        {"id": 2, "text": "Very negative comment :((("},
        {"id": 3, "text": "Neutral comment."},
    ]

    # Call the method with min_polarity filter
    result = await comments_handler.get_comments(
        subfeddit_name="test_subfeddit", min_polarity=0.2, max_polarity=1.0
    )

    # Assertions
    assert len(result) < 3
    for comment in result:
        assert comment["polarity_score"] >= 0.2


@pytest.mark.asyncio
async def test_get_comments_with_sorting(comments_handler):
    """Test CommentsHandler's get_comments method with polarity sorting"""
    # Configure mocks
    comments_handler.db_client.get_subfeddit_id.return_value = 123
    comments_handler.db_client.get_comments.return_value = [
        {"id": 1, "text": "Positive comment!"},
        {"id": 2, "text": "Negative comment :("},
        {"id": 3, "text": "Neutral comment."},
    ]

    # Call the method with polarity_sorting="desc"
    result = await comments_handler.get_comments(
        subfeddit_name="test_subfeddit", polarity_sorting="desc"
    )

    # Assertions
    assert len(result) == 3

    # Check that comments are in descending order of polarity
    for i in range(len(result) - 1):
        assert result[i]["polarity_score"] >= result[i + 1]["polarity_score"]
