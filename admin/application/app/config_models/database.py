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

        if self.skip_indexes == "True":
            self.skip_indexes = True
        else:
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

    async def get_all(self):
        if self.client:
            collection = self.db["users"]
            cursor = collection.find()
            return await cursor.to_list(length=None)
        return None

    async def get_aggregation(self):
        if self.client:
            collection = self.db["users"]

            pipeline = [
                # 1. Match users where level_data is not empty
                {"$match": {"level_data": {"$ne": {}}}},

                # 2. Convert level_data dict to an array of values
                {"$project": {
                    "user_cookie": 1,
                    "user_access_code": 1,
                    "levels_array": {"$objectToArray": "$level_data"}
                }},

                # 3. Count completed levels
                {"$project": {
                    "user_cookie": 1,
                    "user_access_code": 1,
                    "completed_count": {
                        "$size": {
                            "$filter": {
                                "input": "$levels_array.v",
                                "as": "level",
                                "cond": {"$eq": ["$$level.completed", True]}
                            }
                        }
                    },
                    "completed": {
                        "$filter": {
                            "input": "$levels_array.v",
                            "as": "level",
                            "cond": {"$eq": ["$$level.completed", True]}
                        }
                    }
                }},

                {"$sort": {"completed_count": -1}}
            ]
            data = collection.aggregate(pipeline)
            return await data.to_list(length=None)
        return None

    def get_collection(self):
        if self.client:
            return self.db["users"]
        return None

db_config = DatabaseConfig()
