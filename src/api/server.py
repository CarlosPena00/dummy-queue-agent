"""Main server module with FastAPI application."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})


@app.get("/")  # type: ignore[misc]
def to_docs() -> RedirectResponse:
    """Redirect root endpoint to the documentation page."""
    return RedirectResponse("/docs")


@app.get("/ping")  # type: ignore[misc]
def ping_api() -> str:
    """Simple health check endpoint."""
    return "pong"
