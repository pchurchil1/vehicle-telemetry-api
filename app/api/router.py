from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.db_health import router as db_health_router
from app.api.vehicles import router as vehicles_router
from app.api.ecus import router as ecus_router
from app.api.events import router as events_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(db_health_router, tags=["db"])
api_router.include_router(vehicles_router, tags=["vehicles"])
api_router.include_router(ecus_router, tags=["ecus"])
api_router.include_router(events_router, tags=["events"])