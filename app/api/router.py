from fastapi import APIRouter
from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])

from app.api.db_health import router as db_health_router
api_router.include_router(db_health_router, tags=["db"])

from app.api.vehicles import router as vehicles_router
api_router.include_router(vehicles_router, tags=["vehicles"])