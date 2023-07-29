from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})


@app.get("/")
def to_docs():
    return RedirectResponse("/docs")
