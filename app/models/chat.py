from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None
    model_used: Optional[str] = None

class CreateSessionRequest(BaseModel):
    pass

class CreateSessionResponse(BaseModel):
    session_id: str
    created_at: str

class ChatHistoryRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to retrieve history for")

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    total_count: int

class SaveChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    user_message: str = Field(..., description="User's message")
    gemini_response: str = Field(..., description="AI's response")
