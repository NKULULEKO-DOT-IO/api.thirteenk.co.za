import asyncio
import os
import sys
from io import BytesIO

# Add project root to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.storage_service import StorageService
from app.core.config import get_settings
from app.core.logging import logger


class SimpleUploadFile:
    """A simple class that mimics FastAPI's UploadFile just enough for our test"""

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


async def test_upload_specific_image(image_path):
    """
    Test uploading a specific image file to Google Cloud Storage.

    Args:
        image_path: Path to the image file to upload
    """
    logger.info(f"Starting upload test for image: {image_path}")

    # Verify file exists
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        print(f"Error: Image file not found at {image_path}")
        return None

    # Get file info
    file_size = os.path.getsize(image_path)
    file_name = os.path.basename(image_path)

    logger.info(f"Image file size: {file_size} bytes")

    # Get settings
    settings = get_settings()
    logger.info(f"Using project ID: {settings.GCS_PROJECT_ID}")
    logger.info(f"Using original bucket: {settings.GCS_ORIGINAL_BUCKET}")
    logger.info(f"Using thumbnail bucket: {settings.GCS_THUMBNAIL_BUCKET}")

    try:
        # Create our simple upload file
        upload_file = SimpleUploadFile(image_path)

        # Load file content for thumbnail generation
        with open(image_path, 'rb') as f:
            content = f.read()

        # Initialize storage service
        logger.info("Initializing storage service")
        storage_service = StorageService()

        # Upload image
        logger.info(f"Uploading image with name: {file_name}")
        upload_result = await storage_service.upload_image(upload_file)
        logger.info(f"Upload successful: {upload_result}")

        # Generate thumbnail
        logger.info("Generating thumbnail")
        thumbnail_url = await storage_service.generate_thumbnail(upload_result["filename"], content)
        logger.info(f"Thumbnail generated: {thumbnail_url}")

        # Print URLs for verification
        print(f"\nOriginal image URL: {upload_result['hd_url']}")
        print(f"Thumbnail URL: {thumbnail_url}")

        # Return the filename so we can clean it up later if needed
        return upload_result["filename"]

    except Exception as e:
        logger.error(f"Upload test failed with error: {e}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def delete_test_image(filename):
    """Delete the test image from cloud storage."""
    logger.info(f"Deleting test image: {filename}")
    storage_service = StorageService()
    result = await storage_service.delete_image(filename)
    logger.info(f"Deletion result: {result}")


async def main():
    """Run the upload test for the specific image file."""
    # Set path to the image file - change this to the actual path if needed
    image_path = "IMG_4711.JPEG"  # Assuming it's in the current directory

    try:
        filename = await test_upload_specific_image(image_path)

        if filename:
            # Ask user if they want to keep or delete the test image
            keep_image = input("\nImage uploaded successfully. Keep the image in cloud storage? (y/n): ")
            if keep_image.lower() != 'y':
                await delete_test_image(filename)
                print(f"Image {filename} deleted from cloud storage.")
            else:
                print(f"Image kept in cloud storage with filename: {filename}")

            print("\nTest completed successfully!")
        else:
            print("\nTest failed - could not upload image.")
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {e}")
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())