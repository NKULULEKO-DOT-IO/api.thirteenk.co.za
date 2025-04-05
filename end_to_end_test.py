import asyncio
import os
import sys
import json
from datetime import datetime

# Add project root to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongodb import connect_to_mongodb, close_mongodb_connection
from app.core.config import get_settings
from app.core.logging import logger
from app.services.image_service import ImageService
from app.services.download_service import DownloadService


class SimpleUploadFile:
    """A simple class that mimics FastAPI's UploadFile for testing"""

    def __init__(self, filepath):
        self.filename = os.path.basename(filepath)
        self._filepath = filepath

        # Determine content type based on file extension
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            self.content_type = "image/jpeg"
        elif ext in ['.png']:
            self.content_type = "image/png"
        elif ext in ['.gif']:
            self.content_type = "image/gif"
        else:
            self.content_type = "application/octet-stream"

        # Load the file content
        with open(filepath, 'rb') as f:
            self._content = f.read()

    async def read(self):
        """Return the file content"""
        return self._content

    async def seek(self, offset):
        """Pretend to seek in the file"""
        pass





async def run_end_to_end_test(image_path):
    """
    Run an end-to-end test that:
    1. Connects to MongoDB
    2. Uploads an image to GCS using credentials from environment variable
    3. Creates a database entry for the image
    4. Records a download for the image
    5. Retrieves the image and download count
    6. Cleans up (optional)
    """
    logger.info("Starting end-to-end test")

    try:
        # Step 2: Connect to MongoDB
        logger.info("Connecting to MongoDB")
        await connect_to_mongodb()

        # Step 3: Create services
        logger.info("Initializing services")
        image_service = ImageService()
        download_service = DownloadService()

        # Step 4: Test uploading image
        logger.info(f"Uploading test image: {image_path}")
        upload_file = SimpleUploadFile(image_path)

        image_data = {
            "name": "Test Image from End-to-End Test",
            "description": "This is an image uploaded during an end-to-end test",
            "tags": ["test", "e2e", "automation"],
            "is_featured": True
        }

        image = await image_service.create_image(upload_file, image_data)
        logger.info(f"Image created with ID: {image.id}")

        # Step 5: Test retrieving image
        logger.info(f"Retrieving image with ID: {image.id}")
        retrieved_image = await image_service.get_image(image.id)
        logger.info(f"Retrieved image: {retrieved_image.name}")

        # Step 6: Test recording a download
        logger.info(f"Recording download for image: {image.id}")
        request_info = {
            "ip_address": "127.0.0.1",
            "user_agent": "End-to-End Test",
            "referer": "e2e_test.py",
            "country_code": "US"
        }

        download = await download_service.record_download(image.id, request_info)
        logger.info(f"Download recorded with ID: {download.id}")

        # Step 7: Test getting download count
        logger.info(f"Getting download count for image: {image.id}")
        download_count = await download_service.get_image_downloads(image.id)
        logger.info(f"Download count: {download_count}")

        # Step 8: Display results
        print("\n=== End-to-End Test Results ===")
        print(f"Image ID: {image.id}")
        print(f"Image Name: {image.name}")
        print(f"Original Image URL: {image.hd_url}")
        print(f"Thumbnail URL: {image.thumbnail_url}")
        print(f"Image Tags: {', '.join(image.tags)}")
        print(f"Image Downloads: {download_count}")
        print("==============================\n")

        # Step 9: Ask if user wants to clean up
        keep_data = input("Keep the test data in the database and storage? (y/n): ")
        if keep_data.lower() != 'y':
            logger.info("Cleaning up test data")
            await image_service.delete_image(image.id)
            logger.info("Test data cleaned up")
            print("Test data has been deleted.")
        else:
            logger.info("Test data kept")
            print("Test data has been kept in the database and storage.")

        return True

    except Exception as e:
        logger.error(f"End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Step 10: Close MongoDB connection
        await close_mongodb_connection()


async def main():
    """Run the end-to-end test."""
    image_path = "IMG_4711.JPEG"  # Change this to the path of your test image

    if not os.path.exists(image_path):
        print(f"ERROR: Image file not found: {image_path}")
        return

    result = await run_end_to_end_test(image_path)

    if result:
        print("End-to-end test completed successfully!")
    else:
        print("End-to-end test failed!")


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())