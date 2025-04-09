from fastapi import FastAPI

from app.endpoints import comments

# Creating an instance of the FastAPI application
app = FastAPI()

# Including the 'comments' router into the main FastAPI application, which adds all routes from 'comments' to the app
app.include_router(comments.router)


@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to Feddit API"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint to check if the API is running smoothly.

    Returns:
        dict: A dictionary with the status of the application, which is 'ok' when healthy.
    """
    return {"status": "ok"}
