from fastapi import APIRouter
from app.api import chat, history

api_router = APIRouter()

api_router.include_router(
    chat.router,
    tags=["chat"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    history.router,
    tags=["history"],
    responses={404: {"description": "Not found"}}
)