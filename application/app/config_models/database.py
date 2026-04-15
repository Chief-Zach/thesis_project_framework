from dotenv import load_dotenv
from typing import Optional
from pymongo import AsyncMongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.models import initialize_models
from loguru import logger
import os

load_dotenv()


class DatabaseConfig:
    """Database configuration and connection management"""

    def __init__(self):
        self.connection_string = os.getenv('MONGODB_URI')
        self.database_name = os.getenv('DATABASE_NAME')
        self.skip_indexes = os.getenv('SKIP_INDEXES')

        if self.skip_indexes is None or self.skip_indexes == "False":
            self.skip_indexes = False

        self.client: Optional[AsyncMongoClient] = None
        self.db = None

    async def connect(self) -> AsyncIOMotorClient:
        """Establish database connection"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string, tz_aware=True)
            self.db = self.client[self.database_name]

            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {self.database_name}")

            if await initialize_models.init_database(self.db, self.skip_indexes):
                logger.info("Successfully initialized models")

            else:
                logger.error("Could not initialize models")
                raise

            return self.client

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from MongoDB")

db_config = DatabaseConfig()
