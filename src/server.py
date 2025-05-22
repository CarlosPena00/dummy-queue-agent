from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})


@app.get("/")
def to_docs() -> RedirectResponse:  # type: ignore[no-any-unimported]
    return RedirectResponse("/docs")


@app.get("/ping")
def ping_api() -> str:
    return "pong"
