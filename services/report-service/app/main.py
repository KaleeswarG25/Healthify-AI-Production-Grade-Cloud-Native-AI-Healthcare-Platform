from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import report_routes


app = FastAPI(
    title="AI Health Report Service",
    description="Medical report storage and management service",
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
    report_routes.router,
    prefix="/api",
    tags=["reports"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Health Report Service",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "report-service",
    }