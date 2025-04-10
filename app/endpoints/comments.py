import traceback
from contextlib import asynccontextmanager
from typing import List, Literal, Optional

from fastapi import APIRouter, FastAPI, HTTPException

from app.handlers.comments_handler import CommentsHandler
from app.schemas.comment_schema import Comment

# Creating an instance of CommentsHandler to handle comment-related functionality
comments_handler = CommentsHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to DB
    await comments_handler.db_client.connect_to_db()
    yield


# Creating an instance of APIRouter to define routes in the application
router = APIRouter(lifespan=lifespan)


@router.get("/comments", response_model=List[Comment])
async def get_comments(
    subfeddit_name: str,
    n_comments: Optional[int] = 25,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    polarity_sorting: Optional[Literal["asc", "desc"]] = None,
    min_polarity: Optional[float] = -1,
    max_polarity: Optional[float] = 1,
):
    """
    Fetches a list of comments for a given subfeddit with optional filters such as date range, polarity range, and sorting.

    Args:
        subfeddit_name (str): The name of the subfeddit whose comments are to be fetched.
        n_comments (Optional[int]): The number of comments to retrieve. Default is 25.
        from_date (Optional[str]): The start date for filtering comments (optional).
        to_date (Optional[str]): The end date for filtering comments (optional).
        polarity_sorting (Optional[Literal["asc", "desc"]]): Sorting order for comments by polarity (optional).
        min_polarity (Optional[float]): Minimum polarity value for filtering comments (default is -1).
        max_polarity (Optional[float]): Maximum polarity value for filtering comments (default is 1).

    Returns:
        List[Comment]: A list of comments that match the filtering criteria.

    Raises:
        HTTPException: If an unexpected error occurs during the process, a 500 error is raised.
    """
    try:
        # Call the CommentsHandler's get_comments method to fetch the comments with the specified filters
        comments = await comments_handler.get_comments(
            subfeddit_name=subfeddit_name,
            from_date=from_date,
            to_date=to_date,
            polarity_sorting=polarity_sorting,
            n_comments=n_comments,
            min_polarity=min_polarity,
            max_polarity=max_polarity,
        )
    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )

    return comments
