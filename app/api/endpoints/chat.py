import logging
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatMessage, ChatResponse
from app.services.gemini import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def gemini_chat(message: ChatMessage) -> ChatResponse:
    try:
        logger.info(f"Received chat request: {message.message}")

        response = await gemini_service.generate_response(message.message)
        if response.error:
            logger.warning(f"Chat request failed: {response.error}")
        else:
            logger.info("Chat request processed")

        return response

    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
