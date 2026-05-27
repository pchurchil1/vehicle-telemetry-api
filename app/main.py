from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.schemas.error import ErrorOut

def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        responses={
            401: {"model": ErrorOut},
            404: {"model": ErrorOut},
            409: {"model": ErrorOut},
            422: {"model": ErrorOut},
        },
    )
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def root():
        return {"service": settings.app_name, "environment": settings.environment}

    return app

app = create_app()
