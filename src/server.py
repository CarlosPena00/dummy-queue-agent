"""Main server module with FastAPI application."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})


@app.get("/")
def to_docs() -> RedirectResponse:
    """Redirect root endpoint to the documentation page."""
    return RedirectResponse("/docs")


@app.get("/ping")
def ping_api() -> str:
    """Simple health check endpoint."""
    return "pong"
