"""
FastAPI Application Factory

Creates and configures the FastAPI application with middleware,
exception handlers, and core endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.utils.logging import setup_logging
from .routes import router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # Setup logging
    setup_logging(settings.LOG_LEVEL)

    # Create app
    app = FastAPI(
        title=settings.APP_NAME,
        description="Context-Aware Question Generation Tool - Aggregates context from multiple sources and generates clarification questions",
        version="0.1.0",
        debug=settings.DEBUG,
    )

    logger.info(f"Creating FastAPI application: {settings.APP_NAME}")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("Added CORS middleware")

    # Include routes
    app.include_router(router)
    logger.debug("Included API routes")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "app": settings.APP_NAME,
        }

    # MCP listing endpoint
    @app.get("/mcps")
    async def list_mcps():
        """List configured MCPs"""
        from src.mcp_integration import MCPManager

        try:
            manager = MCPManager()
            mcps = manager.list_mcps()
            counts = manager.registry.count_mcps()

            return {
                "mcps": mcps,
                "statistics": {
                    "total": counts["total"],
                    "enabled": counts["enabled"],
                    "disabled": counts["disabled"],
                },
            }
        except Exception as e:
            logger.error(f"Error listing MCPs: {e}")
            return {
                "error": str(e),
                "mcps": [],
                "statistics": {"total": 0, "enabled": 0, "disabled": 0},
            }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
            "endpoints": {
                "health": "/health",
                "mcps": "/mcps",
                "analyze": "/analyze",
                "docs": "/docs",
            },
        }

    logger.info("FastAPI application created successfully")

    return app


# Create application instance
app = create_app()
