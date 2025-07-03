import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatHistoryRequest, ChatHistoryResponse, SaveChatMessageRequest
from app.services.chat_history import chat_history_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(session_id: str):
    try:
        history = chat_history_service.get_chat_history(session_id=session_id)
        return history
    
    except Exception as e:
        error_msg = f"Failed to retrieve chat history: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/sessions")
def get_all_sessions():
    try:
        sessions = chat_history_service.get_all_sessions()
        
        return {
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        error_msg = f"Failed to retrieve sessions: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) 