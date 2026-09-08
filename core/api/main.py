"""
Main FastAPI Application Factory.

Creates and configures the FastAPI application with all middleware,
routes, error handlers, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from infrastructure.logsys.structured import get_logger

# Import routes
try:
    from core.api.routes import health, chat, agents, system
    ROUTES_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    ROUTES_AVAILABLE = False

logger = get_logger(__name__)


class ApplicationConfig:
    """Application configuration."""
    title = "JARVIS Super Intelligence Platform"
    description = "Advanced AI Assistant with Automation, Voice Interaction, and Task Management"
    version = "0.2.0"
    docs_url = "/docs"
    openapi_url = "/openapi.json"
    redoc_url = "/redoc"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting JARVIS {ApplicationConfig.version}...")
    
    try:
        logger.info("Core services initialized")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down JARVIS...")
    logger.info("JARVIS shutdown completed")


def create_application(config: Optional[ApplicationConfig] = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        config: Optional application configuration
    
    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = ApplicationConfig()
    
    app = FastAPI(
        title=config.title,
        description=config.description,
        version=config.version,
        docs_url=config.docs_url,
        openapi_url=config.openapi_url,
        redoc_url=config.redoc_url,
        lifespan=lifespan,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    # Include routers if available
    if ROUTES_AVAILABLE:
        app.include_router(health.router, prefix="/api/v1", tags=["Health"])
        app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
        app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
        app.include_router(system.router, prefix="/api/v1", tags=["System"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "application": config.title,
            "version": config.version,
            "status": "running",
            "docs": config.docs_url,
        }
    
    @app.get("/health", status_code=status.HTTP_200_OK)
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "JARVIS"}
    
    logger.info(f"FastAPI application created: {config.title} v{config.version}")
    return app


if __name__ == "__main__":
    app = create_application()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
    )
