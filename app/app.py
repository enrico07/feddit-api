from fastapi import FastAPI

from app.endpoints import comments

app = FastAPI()

app.include_router(comments.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Feddit API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
