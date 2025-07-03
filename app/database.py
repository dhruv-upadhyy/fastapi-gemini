import os
import logging
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: MongoClient
        self.database: Database
        self.chat_sessions: Collection
        self.chat_history: Collection

db_manager = DatabaseManager()

def connect_to_mongo():
    try:
        mongodb_url = os.getenv("MONGODB_URL")
        database_name = os.getenv("DATABASE_NAME")

        logger.info(f"Connecting to MongoDB at {mongodb_url}")

        db_manager.client = MongoClient(mongodb_url)

        if database_name:
            db_manager.database = db_manager.client[database_name]

        db_manager.chat_sessions = db_manager.database.chat_sessions
        db_manager.chat_history = db_manager.database.chat_history

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    return db_manager.database

def get_chat_sessions_collection():
    return db_manager.chat_sessions

def get_chat_history_collection():
    return db_manager.chat_history 