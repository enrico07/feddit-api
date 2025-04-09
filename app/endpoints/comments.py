import traceback
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException

from app.handlers.comments_handler import CommentsHandler
from app.schemas.comment_schema import Comment

router = APIRouter()
comments_handler = CommentsHandler()


@router.get("/comments", response_model=List[Comment])
def get_comments(
    subfeddit_name: str,
    n_comments: Optional[int] = 25,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    polarity_sorting: Optional[Literal["asc", "desc"]] = None,
    min_polarity: Optional[float] = -1,
    max_polarity: Optional[float] = 1,
):
    try:
        comments = comments_handler.get_comments(
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
