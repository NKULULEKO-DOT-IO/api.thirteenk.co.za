from datetime import datetime
from typing import List, Optional, Dict, Any

from bson import ObjectId
from fastapi import UploadFile

from src.db.mongodb import get_database
from src.models.image import Image
from src.services.storage_service import StorageService
from src.core.logging import logger
from src.core.exceptions import ImageNotFoundException


class ImageService:
    """Service for handling image operations."""

    def __init__(self):
        """Initialize the image service."""
        self.db = get_database()
        self.storage_service = StorageService()

    async def get_images(
            self,
            skip: int = 0,
            limit: int = 20,
            tags: Optional[List[str]] = None,
            is_featured: Optional[bool] = None
    ) -> List[Image]:
        """Get a list of images with optional filtering."""
        # Build query
        query = {}
        if tags:
            query["tags"] = {"$all": tags}
        if is_featured is not None:
            query["is_featured"] = is_featured

        # Execute query
        cursor = self.db.images.find(query).skip(skip).limit(limit).sort("created_at", -1)
        images = await cursor.to_list(length=limit)

        # Convert to Image model
        return [Image(**doc) for doc in images]

    async def count_images(
            self,
            tags: Optional[List[str]] = None,
            is_featured: Optional[bool] = None
    ) -> int:
        """Count total images with optional filtering."""
        # Build query
        query = {}
        if tags:
            query["tags"] = {"$all": tags}
        if is_featured is not None:
            query["is_featured"] = is_featured

        # Execute count
        return await self.db.images.count_documents(query)

    async def get_image(self, image_id: str) -> Image:
        """Get a single image by ID."""
        try:
            doc = await self.db.images.find_one({"_id": ObjectId(image_id)})
            if not doc:
                raise ImageNotFoundException()
            return Image(**doc)
        except Exception as e:
            logger.error(f"Error getting image {image_id}: {e}")
            raise ImageNotFoundException()

    async def create_image(self, file: UploadFile, image_data: Dict[str, Any]) -> Image:
        """Create a new image."""
        try:
            # Upload to storage
            storage_data = await self.storage_service.upload_image(file)

            # Generate thumbnail
            content = await file.seek(0)
            content = await file.read()
            thumbnail_url = await self.storage_service.generate_thumbnail(
                storage_data["filename"],
                content
            )

            # Prepare image data
            new_image = {
                "name": image_data["name"],
                "description": image_data.get("description", ""),
                "filename": storage_data["filename"],
                "thumbnail_url": thumbnail_url,
                "hd_url": storage_data["hd_url"],
                "file_size": storage_data["file_size"],
                "content_type": storage_data["content_type"],
                "tags": image_data.get("tags", []),
                "downloads": 0,
                "created_at": datetime.utcnow(),
                "is_featured": image_data.get("is_featured", False)
            }

            # Insert into database
            result = await self.db.images.insert_one(new_image)
            new_image["_id"] = result.inserted_id

            logger.info(f"Created new image with ID {result.inserted_id}")

            return Image(**new_image)
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            raise

    async def update_image(self, image_id: str, image_data: Dict[str, Any]) -> Image:
        """Update an existing image."""
        try:
            # Check if image exists
            image = await self.get_image(image_id)

            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow(),
                **{k: v for k, v in image_data.items() if v is not None}
            }

            # Update in database
            await self.db.images.update_one(
                {"_id": ObjectId(image_id)},
                {"$set": update_data}
            )

            logger.info(f"Updated image {image_id}")

            # Return updated image
            return await self.get_image(image_id)
        except Exception as e:
            logger.error(f"Error updating image {image_id}: {e}")
            raise

    async def delete_image(self, image_id: str) -> bool:
        """Delete an image."""
        try:
            # Check if image exists
            image = await self.get_image(image_id)

            # Delete from storage
            await self.storage_service.delete_image(image.filename)

            # Delete from database
            result = await self.db.images.delete_one({"_id": ObjectId(image_id)})

            logger.info(f"Deleted image {image_id}")

            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {e}")
            raise