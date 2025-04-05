from src.db.mongodb import get_database
from src.core.logging import logger


async def init_db():
    """Initialize database with required collections and indexes."""
    db = get_database()

    # Create collections if they don't exist
    collections = await db.list_collection_names()

    if "images" not in collections:
        logger.info("Creating images collection")
        await db.create_collection("images")

    if "downloads" not in collections:
        logger.info("Creating downloads collection")
        await db.create_collection("downloads")

    # Create indexes
    logger.info("Setting up indexes")

    # Images collection indexes
    await db.images.create_index("name")
    await db.images.create_index("tags")
    await db.images.create_index("created_at")
    await db.images.create_index("is_featured")

    # Downloads collection indexes
    await db.downloads.create_index("image_id")
    await db.downloads.create_index("timestamp")
    await db.downloads.create_index("ip_address")

    logger.info("Database initialization completed")