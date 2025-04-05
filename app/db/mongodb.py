from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongodb():
    """Connect to MongoDB."""
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        logger.info("Client created, connecting to database...")
        mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
        logger.info(f"Connected to database {settings.MONGODB_DB_NAME}, pinging...")
        # Ping the database to verify connection --
        await mongodb.db.command("ping")
        logger.info("Connected to MongoDB successfully")
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise

async def close_mongodb_connection():
    """Close MongoDB connection."""
    logger.info("Closing MongoDB connection...")
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance."""
    return mongodb.db