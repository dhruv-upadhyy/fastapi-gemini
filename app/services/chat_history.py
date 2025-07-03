import logging
from typing import List, Optional
from datetime import datetime
from app.models.chat import ChatHistoryResponse
from app.database import get_chat_sessions_collection, get_chat_history_collection

logger = logging.getLogger(__name__)

class ChatHistoryService:

    def create_or_update_session(self, session_id: str) -> dict:
        try:
            sessions_collection = get_chat_sessions_collection()
            
            existing_session = sessions_collection.find_one({"session_id": session_id})
            
            if existing_session:
                sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$set": {"last_activity": datetime.utcnow()}}
                )
                logger.info(f"Updated session {session_id}")
                return existing_session
            else:
                new_session = {
                    "session_id": session_id,
                    "created_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow(),
                    "message_count": 0
                }
                sessions_collection.insert_one(new_session)
                logger.info(f"Created new session {session_id}")
                return new_session
                
        except Exception as e:
            logger.error(f"Error creating/updating session {session_id}: {str(e)}")
            raise
    
    def save_chat_message(
        self, 
        session_id: str, 
        user_message: str, 
        gemini_response: str, 
        model_used: Optional[str] = None
    ) -> dict:
        try:
            history_collection = get_chat_history_collection()
            sessions_collection = get_chat_sessions_collection()
            
            chat_entry = {
                "session_id": session_id,
                "user_message": user_message,
                "gemini_response": gemini_response,
                "timestamp": datetime.utcnow(),
                "model_used": model_used
            }
            
            result = history_collection.insert_one(chat_entry)
            chat_entry["_id"] = result.inserted_id
            
            sessions_collection.update_one(
                {"session_id": session_id},
                {
                    "$inc": {"message_count": 1},
                    "$set": {"last_activity": datetime.utcnow()}
                }
            )
            
            logger.info(f"Saved chat message for session {session_id}")
            return chat_entry
            
        except Exception as e:
            logger.error(f"Error saving chat message for session {session_id}: {str(e)}")
            raise
    
    def get_chat_history(self, session_id: str) -> ChatHistoryResponse:
        try:
            history_collection = get_chat_history_collection()
            
            total_count = history_collection.count_documents({"session_id": session_id})
            
            cursor = history_collection.find({"session_id": session_id}).sort("timestamp", 1)

            messages = list(cursor)
            
            message_dicts = []
            for msg in messages:
                message_dicts.append({
                    "user_message": msg["user_message"],
                    "gemini_response": msg.get("gemini_response", msg.get("ai_response", "")),
                    "timestamp": msg["timestamp"].isoformat(),
                    "model_used": msg.get("model_used")
                })
            
            return ChatHistoryResponse(
                session_id=session_id,
                messages=message_dicts,
                total_count=total_count
            )
            
        except Exception as e:
            logger.error(f"Error retrieving chat history for session {session_id}: {str(e)}")
            raise
    
    def get_all_sessions(self) -> List[dict]:
        try:
            sessions_collection = get_chat_sessions_collection()
            
            cursor = sessions_collection.find().sort("last_activity", -1)
            
            sessions = list(cursor)
            
            session_list = []
            for session in sessions:
                session_list.append({
                    "session_id": session["session_id"],
                    "created_at": session["created_at"].isoformat(),
                    "last_activity": session["last_activity"].isoformat(),
                    "message_count": session["message_count"]
                })
            
            logger.info(f"Retrieved {len(sessions)} sessions")
            return session_list
            
        except Exception as e:
            logger.error(f"Error retrieving sessions: {str(e)}")
            raise

chat_history_service = ChatHistoryService() 