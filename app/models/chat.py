from typing import Optional
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
