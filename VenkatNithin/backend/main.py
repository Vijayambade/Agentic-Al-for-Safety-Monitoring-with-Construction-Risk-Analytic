"""
backend/main.py
---------------
Main entry point for the FastAPI backend application.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import close_mongo, init_db
from backend.routers.auth import router as auth_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.ai import router as ai_router
from backend.routers.document_analyzer import router as document_analyzer_router
from backend.routers.safety import router as safety_router
from backend.routers.safety_monitoring import router as safety_monitoring_router
from backend.routers.schedule import router as schedule_router
from backend.routers.telematics import router as telematics_router
from backend.routers.inventory import router as inventory_router
from backend.routers.waste import router as waste_router
from backend.routers.noise import router as noise_router
from backend.routers.air_quality import router as air_quality_router
from backend.routers.water import router as water_router
from backend.routers.structural import router as structural_router
from backend.routers.energy import router as energy_router
from backend.routers.weather import router as weather_router
from backend.routers.material_estimation import router as material_estimation_router
import backend.models  # Ensure all models are registered on Base metadata

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI startup and shutdown."""
    logger.info("Initializing Construction Intelligent Hub database...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Cleaning up database connections...")
    await close_mongo()
    logger.info("Database connections closed.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API services for AI Powered Construction Management & Intelligent Hiring Platform",
    lifespan=lifespan,
)

# CORS Configuration
# Allow local Streamlit server to communicate with APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # default streamlit port
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(ai_router)
app.include_router(document_analyzer_router)
app.include_router(safety_router)
app.include_router(safety_monitoring_router)
app.include_router(schedule_router)
app.include_router(telematics_router)
app.include_router(inventory_router)
app.include_router(waste_router)
app.include_router(noise_router)
app.include_router(air_quality_router)
app.include_router(water_router)
app.include_router(structural_router)
app.include_router(energy_router)
app.include_router(weather_router)
app.include_router(material_estimation_router)

# Mount static folder for text-to-speech audio files
os.makedirs("./data/cache", exist_ok=True)
app.mount("/cache", StaticFiles(directory="./data/cache"), name="cache")


@app.get("/health", tags=["Health"])
def health_check():
    """Verify application health and versioning information."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
