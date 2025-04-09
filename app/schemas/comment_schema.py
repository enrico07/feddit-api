from pydantic import BaseModel


class Comment(BaseModel):
    id: int
    text: str
    polarity_score: float
    polarity_classification: str
