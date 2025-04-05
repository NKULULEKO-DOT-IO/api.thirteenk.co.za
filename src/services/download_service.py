from datetime import datetime
from typing import Dict, Any

from bson import ObjectId

from src.db.mongodb import get_database
from src.models.download import Download
from src.core.logging import logger


class DownloadService:
    """Service for handling download operations."""

    def __init__(self):
        """Initialize the download service."""
        self.db = get_database()

    async def record_download(self, image_id: str, request_info: Dict[str, Any]) -> Download:
        """Record a download event."""
        try:
            # Increment image download counter
            await self.db.images.update_one(
                {"_id": ObjectId(image_id)},
                {"$inc": {"downloads": 1}}
            )

            # Record download details
            download_data = {
                "image_id": image_id,
                "ip_address": request_info.get("ip_address", "unknown"),
                "user_agent": request_info.get("user_agent", "unknown"),
                "referer": request_info.get("referer"),
                "country_code": request_info.get("country_code"),
                "timestamp": datetime.utcnow()
            }

            result = await self.db.downloads.insert_one(download_data)
            download_data["_id"] = result.inserted_id

            logger.info(f"Recorded download for image {image_id}")

            return Download(**download_data)
        except Exception as e:
            logger.error(f"Error recording download: {e}")
            raise

    async def get_total_downloads(self) -> int:
        """Get total downloads across all images."""
        try:
            pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$downloads"}}}
            ]
            result = await self.db.images.aggregate(pipeline).to_list(length=1)
            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Error getting total downloads: {e}")
            raise

    async def get_image_downloads(self, image_id: str) -> int:
        """Get download count for a specific image."""
        try:
            image = await self.db.images.find_one(
                {"_id": ObjectId(image_id)},
                {"downloads": 1}
            )
            return image["downloads"] if image else 0
        except Exception as e:
            logger.error(f"Error getting image downloads: {e}")
            raise
