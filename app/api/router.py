
from fastapi import APIRouter
from app.api import chat

api_router = APIRouter()

api_router.include_router(
    chat.router,
    tags=["chat"],
    responses={404: {"description": "Not found"}}
)