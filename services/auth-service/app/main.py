from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth_routes


app = FastAPI(
    title="AI Health Authentication Service",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["authentication"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Health Authentication Service",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "auth-service",
    }