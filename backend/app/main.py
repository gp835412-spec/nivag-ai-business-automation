"""
NIVAG AI Business Automation
Application Entry Point

Production ASGI application bootstrap.

Responsibilities:
- Create the FastAPI application.
- Load centralized application settings.
- Configure application metadata.
- Configure CORS.
- Register API routers.
- Provide the application object for ASGI servers.

Business logic, database operations, and API endpoint
implementation do not belong in this module.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.companies import router as companies_router
from app.api.v1.contacts import router as contacts_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.users import router as users_router
from app.core.config import settings


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI application instance.
    """

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        auth_router,
        prefix="/api/v1",
    )

    application.include_router(
        users_router,
        prefix="/api/v1",
    )

    application.include_router(
        organizations_router,
        prefix="/api/v1",
    )

    application.include_router(
        companies_router,
        prefix="/api/v1",
    )

    application.include_router(
        contacts_router,
        prefix="/api/v1",
    )

    return application


app = create_application()


__all__ = [
    "app",
    "create_application",
]