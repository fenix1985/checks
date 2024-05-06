from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.staticfiles import StaticFiles

from api.routers import api_router

from core.config import settings

app = FastAPI(
    title="payment application",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

add_pagination(app)

app.include_router(api_router, prefix=settings.API_PREFIX)
