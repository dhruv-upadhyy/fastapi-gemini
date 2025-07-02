import json
import uuid
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatMessage, ChatResponse
from app.services.gemini import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()

pending_messages = {}

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

@router.post("/chat/stream")
async def gemini_chat_stream_post(message: ChatMessage):
    try:
        session_id = str(uuid.uuid4())
        pending_messages[session_id] = message.message
        
        return {"session_id": session_id}

    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/chat/stream/{session_id}")
async def gemini_chat_stream_sse(session_id: str):
    try:
        message = pending_messages.pop(session_id)

        async def generate_sse_stream():
            try:
                async for chunk in gemini_service.generate_stream(message):
                    data = json.dumps(chunk)
                    yield f"data: {data}\n\n"
                    
                final_data = json.dumps({"done": True})
                yield f"data: {final_data}\n\n"
                
            except Exception as e:
                error_data = json.dumps({"error": f"Stream error: {str(e)}"})
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
