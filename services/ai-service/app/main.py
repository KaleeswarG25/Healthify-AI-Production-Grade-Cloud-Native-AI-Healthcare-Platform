from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ai_routes


app = FastAPI(
    title="AI Health Service",
    description="Medical report analysis service powered by Ollama",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(
    ai_routes.router,
    prefix="/api/ai",
    tags=["ai"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Health Service",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-service",
    }