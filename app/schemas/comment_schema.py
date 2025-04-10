from pydantic import BaseModel


class Comment(BaseModel):
    id: int
    text: str
    polarity_score: float
    polarity_classification: str


class ErrorResponse(BaseModel):
    detail: str


class HealthCheckResponse(BaseModel):
    status: str


class WelcomeMessage(BaseModel):
    message: str
