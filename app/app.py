from fastapi import FastAPI

from app.endpoints import comments
from app.schemas.comment_schema import HealthCheckResponse, WelcomeMessage

# Creating an instance of the FastAPI application
app = FastAPI(title="Feddit API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

# Including the 'comments' router into the main FastAPI application, which adds all routes from 'comments' to the app
app.include_router(comments.router)


@app.get("/", response_model=WelcomeMessage)
async def root():
    """
    Root endpoint that returns a welcome message.

    Returns:\n
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to Feddit API"}


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to check if the API is running smoothly.

    Returns:\n
        dict: A dictionary with the status of the application, which is 'ok' when healthy.
    """
    return {"status": "ok"}
