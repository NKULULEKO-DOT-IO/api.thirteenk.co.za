import os
import uuid
import json
from io import BytesIO
from typing import Dict, Any, Optional

from fastapi import UploadFile
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image

from app.core.config import get_settings
from app.core.logging import logger
from app.core.exceptions import StorageException

settings = get_settings()


class StorageService:
    """Service for handling Google Cloud Storage operations."""

    def __init__(self):
        """Initialize the storage client and buckets using JSON credentials."""
        try:
            # Get credentials JSON content
            credentials_info = json.loads(settings.GCS_CREDENTIALS_JSON)

            # Create credentials object from JSON
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )

            # Initialize storage client with credentials
            self.client = storage.Client(
                project=settings.GCS_PROJECT_ID,
                credentials=credentials
            )

            self.original_bucket = self.client.bucket(settings.GCS_ORIGINAL_BUCKET)
            self.thumbnail_bucket = self.client.bucket(settings.GCS_THUMBNAIL_BUCKET)

            logger.info("Google Cloud Storage client initialized with JSON credentials")
        except Exception as e:
            logger.error(f"Failed to initialize storage client: {e}")
            raise StorageException(str(e))

    async def upload_image(self, file: UploadFile, filename: Optional[str] = None) -> Dict[str, Any]:
        """Upload an image to Google Cloud Storage."""
        try:
            # Generate unique filename if not provided
            if not filename:
                ext = os.path.splitext(file.filename)[1]
                filename = f"{uuid.uuid4()}{ext}"

            # Read file content
            content = await file.read()
            file_size = len(content)

            # Upload to GCS
            blob = self.original_bucket.blob(filename)
            blob.upload_from_string(
                content,
                content_type=file.content_type
            )

            # Generate public URL
            hd_url = f"https://storage.googleapis.com/{settings.GCS_ORIGINAL_BUCKET}/{filename}"

            logger.info(f"Uploaded image {filename} to storage")

            return {
                "filename": filename,
                "hd_url": hd_url,
                "content_type": file.content_type,
                "file_size": file_size
            }
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            raise StorageException(str(e))

    async def generate_thumbnail(self, filename: str, content: bytes = None) -> str:
        """Generate a thumbnail for an image and upload it to storage."""
        try:
            # If content not provided, download from storage
            if not content:
                blob = self.original_bucket.blob(filename)
                content = blob.download_as_bytes()

            # Generate thumbnail using PIL
            image = Image.open(BytesIO(content))
            image.thumbnail((200, 200))  # Resize to thumbnail size

            # Save thumbnail to memory
            thumbnail_io = BytesIO()
            image_format = image.format or "JPEG"
            image.save(thumbnail_io, format=image_format)
            thumbnail_io.seek(0)

            # Upload thumbnail to storage
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_blob = self.thumbnail_bucket.blob(thumbnail_filename)
            thumbnail_blob.upload_from_file(
                thumbnail_io,
                content_type=f"image/{image_format.lower()}"
            )

            # Generate thumbnail URL
            thumbnail_url = f"https://storage.googleapis.com/{settings.GCS_THUMBNAIL_BUCKET}/{thumbnail_filename}"

            logger.info(f"Generated thumbnail for {filename}")

            return thumbnail_url
        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            raise StorageException(str(e))

    async def delete_image(self, filename: str) -> bool:
        """Delete an image and its thumbnail from storage."""
        try:
            # Delete original image
            original_blob = self.original_bucket.blob(filename)
            if original_blob.exists():
                original_blob.delete()

            # Delete thumbnail
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_blob = self.thumbnail_bucket.blob(thumbnail_filename)
            if thumbnail_blob.exists():
                thumbnail_blob.delete()

            logger.info(f"Deleted image {filename} from storage")

            return True
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            raise StorageException(str(e))