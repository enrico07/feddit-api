import os
import sys
from unittest.mock import patch

import pytest
from fastapi import HTTPException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from app.endpoints.comments import comments_handler, get_comments


@pytest.mark.asyncio
async def test_get_comments_api_success():
    """Test the get_comments API endpoint for successful case"""
    # Mock the CommentsHandler.get_comments method
    with patch.object(comments_handler, "get_comments") as mock_get_comments:
        # Configure the mock to return sample comments
        mock_comments = [
            {
                "id": 1,
                "text": "Great post!",
                "polarity_score": 0.8,
                "polarity_classification": "positive",
            },
            {
                "id": 2,
                "text": "Bad experience.",
                "polarity_score": -0.6,
                "polarity_classification": "negative",
            },
        ]
        mock_get_comments.return_value = mock_comments

        # Call the API endpoint
        result = await get_comments(
            subfeddit_name="test_subfeddit",
            n_comments=2,
            from_date="01-01-2023",
            to_date="31-12-2023",
            polarity_sorting="asc",
            min_polarity=-0.8,
            max_polarity=0.8,
        )

        # Assertions
        mock_get_comments.assert_called_once_with(
            subfeddit_name="test_subfeddit",
            from_date="01-01-2023",
            to_date="31-12-2023",
            polarity_sorting="asc",
            n_comments=2,
            min_polarity=-0.8,
            max_polarity=0.8,
        )
        assert result == mock_comments


@pytest.mark.asyncio
async def test_get_comments_api_error():
    """Test the get_comments API endpoint for error case"""
    # Mock the CommentsHandler.get_comments method to raise an exception
    with patch.object(comments_handler, "get_comments") as mock_get_comments:
        mock_get_comments.side_effect = Exception("Database error")

        # Call the API endpoint and expect HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await get_comments(subfeddit_name="test_subfeddit")

        # Assertions
        assert excinfo.value.status_code == 500
        assert "An unexpected error occurred" in excinfo.value.detail
