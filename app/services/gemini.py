import os
import logging
from typing import Optional, AsyncGenerator
from dotenv import load_dotenv
from google import genai
from google.genai import errors

from app.models.chat import ChatResponse

logger = logging.getLogger(__name__)

load_dotenv()

class GeminiService:
    def __init__(self):
        self.client: Optional[genai.Client] = None
        self.model = os.getenv("GEMINI_MODEL")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._initialize_client()

    def _initialize_client(self) -> None:
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized")

        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")
            self.client = None

    async def generate_response(self, message: str) -> ChatResponse:
        if self.client is None:
            error_msg = "Gemini client is not initialized."
            logger.error(error_msg)
            return ChatResponse(
                response="",
                error=error_msg,
                model_used=None
            )

        try:
            logger.info(f"Generating response for message: {message}")
            
            response = self.client.models.generate_content(
                model=self.model if self.model else "gemini-2.0-flash-001",
                contents=message
            )
            
            return ChatResponse(
                response=response.text or "",
                error=None,
                model_used=self.model
            )
            
        except errors.APIError as e:
            error_msg = f"Gemini API Error: {e.code}: {e.message}"
            logger.error(error_msg)
            
            return ChatResponse(
                response="",
                error=error_msg,
                model_used=self.model
            )
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            
            return ChatResponse(
                response="",
                error=error_msg,
                model_used=self.model
            )

    async def generate_stream(self, message: str) -> AsyncGenerator[dict, None]:
        if self.client is None:
            error_msg = "Gemini client is not initialized."
            logger.error(error_msg)
            yield {"error": error_msg}
            return

        try:            
            response_stream = self.client.models.generate_content_stream(
                model=self.model if self.model else "gemini-2.0-flash-001",
                contents=message
            )

            for chunk in response_stream:
                try:
                    if chunk.text:
                        yield {"content": chunk.text}
                    else:
                        chunk_text = ""
                        if chunk.candidates:
                            for candidate in chunk.candidates:
                                if candidate.content and candidate.content.parts:
                                    for part in candidate.content.parts:
                                        if part.text:
                                            chunk_text += part.text

                        if chunk_text:
                            yield {"content": chunk_text}

                except Exception as chunk_error:
                    logger.warning(f"Error processing chunk: {chunk_error}")
                    continue

            yield {"done": True}
            logger.info("Completed streaming")

        except errors.APIError as e:
            error_msg = f"Gemini API Error: {e.code}: {e.message}"
            logger.error(error_msg)
            yield {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Error during streaming: {str(e)}"
            logger.error(error_msg)
            yield {"error": error_msg}

gemini_service = GeminiService()
