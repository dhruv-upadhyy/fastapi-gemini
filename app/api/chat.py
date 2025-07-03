import json
import uuid
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatMessage, ChatResponse, CreateSessionRequest, CreateSessionResponse
from app.services.gemini import gemini_service
from app.services.chat_history import chat_history_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat/session", response_model=CreateSessionResponse)
async def create_chat_session(request: CreateSessionRequest):
    try:
        session_id = str(uuid.uuid4())
        session = chat_history_service.create_or_update_session(session_id)

        logger.info(f"Created new chat session: {session_id}")

        return CreateSessionResponse(
            session_id=session_id,
            created_at=session["created_at"].isoformat()
        )

    except Exception as e:
        error_msg = f"Failed to create chat session: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/chat/{session_id}", response_model=ChatResponse)
async def gemini_chat(session_id: str, message: ChatMessage) -> ChatResponse:
    try:
        logger.info(f"Received chat request for session {session_id}: {message.message}")

        chat_history_service.create_or_update_session(session_id)

        response = await gemini_service.generate_response(message.message)
        
        if response.error:
            logger.warning(f"Chat request failed for session {session_id}: {response.error}")
        else:
            logger.info(f"Chat request processed successfully for session {session_id}")

            try:
                chat_history_service.save_chat_message(
                    session_id=session_id,
                    user_message=message.message,
                    gemini_response=response.response,
                    model_used=response.model_used
                )
                logger.info(f"Saved chat history for session {session_id}")
            except Exception as save_error:
                logger.error(f"Failed to save chat history for session {session_id}: {str(save_error)}")

        return response

    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/chat/stream/{session_id}")
async def gemini_chat_stream_sse_get(session_id: str, message: str):
    try:
        if not message:
            raise HTTPException(status_code=400, detail="Message parameter is required")
            
        session = chat_history_service.create_or_update_session(session_id)
        if session.get("message_count") != 0:
            past_messages = chat_history_service.get_chat_history(session_id)
            past_messages_str = "\n".join([f"User: {msg['user_message']}\nAI: {msg['gemini_response']}" for msg in past_messages.messages])
            full_session_message = f"Previous messages:\n{past_messages_str}\n\nNew message: {message}"
        else:
            full_session_message = message

        gemini_response_parts = []

        async def generate_sse_stream():
            try:
                async for chunk in gemini_service.generate_stream(full_session_message):
                    if 'content' in chunk:
                        gemini_response_parts.append(chunk['content'])
                    elif 'text' in chunk:
                        gemini_response_parts.append(chunk['text'])

                    data = json.dumps(chunk)
                    yield f"data: {data}\n\n"
                
                complete_ai_response = ''.join(gemini_response_parts)
                if complete_ai_response:
                    try:
                        chat_history_service.save_chat_message(
                            session_id=session_id,
                            user_message=message,
                            gemini_response=complete_ai_response,
                        )
                        logger.info(f"Saved chat history for session {session_id}")
                    except Exception as save_error:
                        logger.error(f"Failed to save chat history: {str(save_error)}")
                    
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
