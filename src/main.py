"""
Application Entry Point

Starts the FastAPI server with Uvicorn.
"""

import logging
from fastapi import FastAPI
import uvicorn

from src.config import settings
from src.fastapi_app.app import app
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Start the application server"""
    setup_logging(settings.LOG_LEVEL)

    logger.info(
        f"Starting {settings.APP_NAME}",
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
