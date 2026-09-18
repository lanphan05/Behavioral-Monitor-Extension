"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api import api_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )
    app.include_router(api_router)
    return app


app = create_app()
