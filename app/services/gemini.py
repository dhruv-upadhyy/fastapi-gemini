import os
import logging
from typing import Optional
from google import genai
from google.genai import errors

from app.models.chat import ChatResponse

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.client: Optional[genai.Client] = None
        self.model = "gemini-2.0-flash-001"
        self.api_key = ""
        self._initialize_client()

    def _initialize_client(self) -> None:
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized")

        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    async def generate_response(self, message: str) -> ChatResponse:
        if not self.is_available():
            error_msg = "Gemini service is not available."
            logger.error(error_msg)
            return ChatResponse(
                response="",
                error=error_msg,
                model_used=None
            )

        try:
            logger.info(f"Generating response for message: {message}")
            
            assert self.client is not None
            response = self.client.models.generate_content(
                model=self.model,
                contents=message
            )
            
            logger.info("Successfully generated response from Gemini")
            
            return ChatResponse(
                response=response.text or "",
                error=None,
                model_used=self.model
            )
            
        except errors.APIError as e:
            error_msg = f"Gemini API Error (Code: {e.code}): {e.message}"
            logger.error(error_msg)
            
            return ChatResponse(
                response="",
                error=error_msg,
                model_used=self.model
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            
            return ChatResponse(
                response="",
                error=error_msg,
                model_used=self.model
            )

gemini_service = GeminiService()
