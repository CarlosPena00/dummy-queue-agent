"""FastAPI server configuration module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger

from src.consumers.stock_consumer import broker
from src.consumers.stock_consumer import router as stock_router
from src.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan.

    Args:
        app: FastAPI application instance

    Yields:
        None: Control back to the application
    """
    _ = app
    try:
        await broker.start()
        logger.info("RabbitMQ broker connected successfully")
        yield
    finally:
        await broker.close()
        logger.info("RabbitMQ broker disconnected")


app = FastAPI(
    title=settings.APP_NAME,
    description="Stock management service with RabbitMQ integration",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"displayRequestDuration": True},
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with versioned prefix
app.include_router(
    stock_router,
    prefix="/api/v1",
    tags=["stock"],
)


@app.get("/")  # type: ignore[misc]
def to_docs() -> RedirectResponse:
    """Redirect root endpoint to the documentation page."""
    return RedirectResponse("/docs")


@app.get("/ping")  # type: ignore[misc]
def ping_api() -> str:
    """Simple health check endpoint."""
    return "pong"
