import logging
from contextlib import asynccontextmanager
from typing import List, Literal, Optional

from fastapi import APIRouter, FastAPI, HTTPException

from app.handlers.comments_handler import CommentsHandler
from app.schemas.comment_schema import Comment, ErrorResponse

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log", mode="a")],
)
logger = logging.getLogger(__name__)

# Creating an instance of CommentsHandler to handle comment-related functionality
comments_handler = CommentsHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to DB
    logger.info("Connecting to the database...")

    await comments_handler.db_client.connect_to_db()
    yield


# Creating an instance of APIRouter to define routes in the application
router = APIRouter(lifespan=lifespan)


@router.get(
    "/comments",
    response_model=List[Comment],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request (Invalid Parameters)",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
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

    Args:\n
        subfeddit_name (str): The name of the subfeddit whose comments are to be fetched.
        n_comments (Optional[int]): The number of comments to retrieve. Default is 25.
        from_date (Optional[str]): The start date for filtering comments (optional). The date format must be DD-MM-YYYY.
        to_date (Optional[str]): The end date for filtering comments (optional). The date format must be DD-MM-YYYY.
        polarity_sorting (Optional[Literal["asc", "desc"]]): Sorting order for comments by polarity (optional). The value can be "asc" for ascending or "desc" for descending order.
        min_polarity (Optional[float]): Minimum polarity value for filtering comments (default is -1). The value must be between -1 and 1.
        max_polarity (Optional[float]): Maximum polarity value for filtering comments (default is 1). The value must be between -1 and 1.

    Returns:\n
        List[Comment]: A list of comments that match the filtering criteria.

    Raises:\n
        HTTPException: If a wrong value is sent as parameter, a 400 error is raised.
        HTTPException: If an unexpected error occurs during the process, a 500 error is raised.
    """
    logger.info(
        f"Fetching comments for subfeddit: {subfeddit_name} with filters: "
        f"n_comments={n_comments}, from_date={from_date}, to_date={to_date}, "
        f"polarity_sorting={polarity_sorting}, min_polarity={min_polarity}, max_polarity={max_polarity}"
    )

    # Ensure min_polarity and max_polarity are within the valid range
    if min_polarity < -1 or min_polarity > 1:
        raise HTTPException(
            status_code=400, detail="min_polarity must be between -1 and 1"
        )

    if max_polarity < -1 or max_polarity > 1:
        raise HTTPException(
            status_code=400, detail="max_polarity must be between -1 and 1"
        )

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
        logger.info(f"Successfully fetched {len(comments)} comments")
    except Exception as e:
        logger.error(f"Error while fetching comments: {str(e)}")

        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )

    return comments
