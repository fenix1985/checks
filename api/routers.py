from fastapi import APIRouter

from api import auth, checks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(checks.router)
