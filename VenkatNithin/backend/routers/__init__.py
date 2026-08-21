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

__all__ = [
    "auth_router",
    "dashboard_router",
    "ai_router",
    "document_analyzer_router",
    "safety_router",
    "safety_monitoring_router",
    "schedule_router",
    "telematics_router",
    "inventory_router",
    "waste_router",
    "noise_router",
    "air_quality_router",
    "water_router",
    "structural_router",
    "energy_router",
    "weather_router",
]
