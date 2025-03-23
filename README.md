# Thirteenk Backend

## Overview

This repository contains the backend API for Thirteenk, a cultural digital content platform focusing on South African imagery. The API is built using FastAPI with MongoDB for data storage, Alembic for migrations, and Google Cloud Storage for image storage with automatic thumbnail generation.

## Technology Stack

- **FastAPI**: High-performance API framework
- **MongoDB**: NoSQL database
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **Google Cloud Storage**: Cloud storage for images
- **Pillow (PIL)**: Image processing for thumbnail generation
- **Motor**: Asynchronous MongoDB driver
- **Python 3.10+**: Programming language

## Prerequisites

- Python 3.10 or higher
- MongoDB 5.0 or higher
- Google Cloud SDK
- Docker and Docker Compose (for containerized deployment)

## Project Structure

```
api.thirteenk.co.za/
├── app/                               # Main application package
│   ├── api/                           # API endpoints
│   │   ├── __init__.py                # Package initialization
│   │   ├── router.py                  # API router configuration
│   │   └── endpoints/                 # API endpoint modules
│   │       ├── __init__.py            # Package initialization
│   │       ├── images.py              # Image endpoints
│   │       ├── downloads.py           # Download endpoints
│   │       └── stats.py               # Statistics endpoints
│   ├── core/                          # Core application components
│   │   ├── __init__.py                # Package initialization
│   │   ├── config.py                  # Application configuration
│   │   ├── security.py                # Authentication utilities
│   │   └── exceptions.py              # Custom exceptions
│   ├── db/                            # Database connections
│   │   ├── __init__.py                # Package initialization
│   │   ├── mongodb.py                 # MongoDB connection utilities
│   │   └── migrations/                # Alembic migrations
│   │       ├── env.py                 # Alembic environment
│   │       ├── script.py.mako         # Alembic script template
│   │       └── versions/              # Migration versions
│   ├── models/                        # Data models
│   │   ├── __init__.py                # Package initialization
│   │   ├── image.py                   # Image model
│   │   └── download.py                # Download model
│   ├── schemas/                       # Pydantic schemas
│   │   ├── __init__.py                # Package initialization
│   │   ├── image.py                   # Image schemas
│   │   └── download.py                # Download schemas
│   ├── services/                      # Service layer
│   │   ├── __init__.py                # Package initialization
│   │   ├── image_service.py           # Image service
│   │   ├── download_service.py        # Download service
│   │   ├── stats_service.py           # Stats service
│   │   └── storage_service.py         # Storage service
│   └── utils/                         # Utility functions
│       ├── __init__.py                # Package initialization
│       ├── image_processing.py        # Image processing utilities
│       └── validators.py              # Custom validators
├── tests/                             # Test directory
│   ├── conftest.py                    # Test configuration
│   ├── test_api/                      # API tests
│   └── test_services/                 # Service tests
├── alembic.ini                        # Alembic configuration
├── main.py                            # Application entry point
├── requirements.txt                   # Package dependencies
└── Dockerfile                         # Docker configuration
```

## Installation and Setup

### Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/thirteenk/backend.git
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google Cloud credentials:
   ```bash
   # Set up application default credentials
   gcloud auth application-default login
   
   # Or set environment variable pointing to service account key
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

5. Create a `.env` file with the following variables:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=thirteenk
   GOOGLE_CLOUD_PROJECT=thirteenk-content
   GOOGLE_CLOUD_BUCKET=thirteenk-images
   CORS_ORIGINS=http://localhost:3000
   SECRET_KEY=your_secret_key_here
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

8. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/images | List all images with pagination |
| GET | /api/images/{id} | Get a specific image by ID |
| POST | /api/images | Create a new image |

### Downloads

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/downloads | Record a download and get a signed URL |

### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/stats | Get platform statistics |

## Key Components

### MongoDB Connection

```python
# app/db/mongodb.py
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoClient:
    client: AsyncIOMotorClient = None
    db = None

mongo = MongoClient()

async def connect_to_mongo():
    """Create database connection."""
    logger.info("Connecting to MongoDB...")
    mongo.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongo.db = mongo.client[settings.DATABASE_NAME]
    
    # Test connection
    try:
        # The ismaster command is cheap and does not require auth
        await mongo.client.admin.command('ismaster')
        logger.info("Connected to MongoDB")
    except ConnectionFailure:
        logger.error("Failed to connect to MongoDB")
        raise

async def close_mongo_connection():
    """Close database connection."""
    logger.info("Closing MongoDB connection...")
    if mongo.client:
        mongo.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    """Return database instance."""
    return mongo.db
```

### Storage Service

The Storage Service handles image uploads and thumbnail generation:

```python
# app/services/storage_service.py
import os
import io
import uuid
import logging
from datetime import datetime, timedelta
from google.cloud import storage
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.exceptions import StorageError

logger = logging.getLogger(__name__)

# Configure Google Cloud Storage client
storage_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
bucket = storage_client.bucket(settings.GOOGLE_CLOUD_BUCKET)


class StorageService:
    @staticmethod
    async def upload_image(file: UploadFile) -> dict:
        """
        Upload an image to Google Cloud Storage and generate thumbnail.
        
        Args:
            file (UploadFile): The uploaded image file
            
        Returns:
            dict: URLs for both original image and thumbnail
        
        Raises:
            StorageError: If upload fails or file is not a valid image
        """
        try:
            content = await file.read()
            
            # Validate image file
            try:
                img = Image.open(io.BytesIO(content))
                img.verify()  # Verify it's a valid image
            except UnidentifiedImageError:
                raise StorageError("Invalid image file")
            
            # Generate a unique filename
            extension = os.path.splitext(file.filename)[1].lower()
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            
            # Original image path
            original_filename = f"original/{timestamp}_{unique_id}{extension}"
            original_blob = bucket.blob(original_filename)
            
            # Upload original
            original_blob.upload_from_string(
                content,
                content_type=file.content_type
            )
            
            # Generate and upload thumbnail
            thumbnail_content = await StorageService.generate_thumbnail(content)
            thumbnail_filename = f"thumbnails/{timestamp}_{unique_id}{extension}"
            thumbnail_blob = bucket.blob(thumbnail_filename)
            thumbnail_blob.upload_from_string(
                thumbnail_content,
                content_type=file.content_type
            )
            
            # Return the URLs
            return {
                "original_url": original_filename,
                "thumbnail_url": thumbnail_filename
            }
            
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise StorageError(f"Failed to upload image: {str(e)}")
    
    @staticmethod
    async def generate_thumbnail(file_content: bytes) -> bytes:
        """
        Generate a thumbnail from image content.
        
        Args:
            file_content (bytes): The original image content
            
        Returns:
            bytes: The thumbnail image content
        """
        # Open the image
        img = Image.open(io.BytesIO(file_content))
        
        # Determine thumbnail size while maintaining aspect ratio
        max_size = (300, 300)
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        return output.getvalue()
```

### Image Service

The Image Service manages image data in the database:

```python
# app/services/image_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.db.mongodb import get_database
from app.schemas.image import ImageCreate, ImageUpdate
from bson.objectid import ObjectId


class ImageService:
    @staticmethod
    async def get_all_images(skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """
        Get all images with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            Dict: Images with pagination info
        """
        db = get_database()
        
        # Get total count
        total = await db.images.count_documents({})
        
        # Get paginated results
        cursor = db.images.find().sort("upload_date", -1).skip(skip).limit(limit)
        images = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for image in images:
            image["id"] = str(image.pop("_id"))
        
        return {
            "images": images,
            "total": total,
            "page": skip // limit + 1,
            "limit": limit
        }
```

### Download Service

The Download Service records download events and generates signed URLs:

```python
# app/services/download_service.py
from datetime import datetime
from typing import List, Dict, Any
from fastapi import Request

from app.db.mongodb import get_database
from app.models.download import DownloadModel
from app.services.image_service import ImageService


class DownloadService:
    @staticmethod
    async def record_download(image_id: str, request: Request) -> Dict[str, Any]:
        """
        Record a new download and increment the image download counter.
        
        Args:
            image_id (str): ID of the downloaded image
            request (Request): The HTTP request
            
        Returns:
            Dict: Download record information with signed URL
        """
        db = get_database()
        
        # Get client information
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Create download record
        download_data = {
            "image_id": image_id,
            "timestamp": datetime.utcnow(),
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        # Insert record
        result = await db.downloads.insert_one(download_data)
        download_id = str(result.inserted_id)
        
        # Increment image download counter
        await ImageService.increment_download_count(image_id)
        
        # Get image details for generating URL
        image = await ImageService.get_image_by_id(image_id)
        
        # Get signed URL for the image
        from app.services.storage_service import StorageService
        signed_url = StorageService.get_signed_url(image["original_url"])
        
        return {
            "id": download_id,
            "image_id": image_id,
            "timestamp": download_data["timestamp"],
            "url": signed_url
        }
```

## Deployment

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t thirteenk-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env.production thirteenk-backend
   ```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    volumes:
      - ./app:/app/app
    depends_on:
      - mongo
    
  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

### Production Environment Variables

For production deployment, set the following environment variables:

```
MONGODB_URL=mongodb://mongo:27017
DATABASE_NAME=thirteenk
GOOGLE_CLOUD_PROJECT=thirteenk-content
GOOGLE_CLOUD_BUCKET=thirteenk-images
CORS_ORIGINS=https://thirteenk.co.za
SECRET_KEY=your_production_secret_key
```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints for function parameters and return values
   - Document all functions with docstrings
   - Use meaningful variable and function names

2. **API Development**
   - Follow RESTful API design principles
   - Use proper HTTP status codes
   - Implement proper error handling
   - Use Pydantic for request and response validation

3. **Testing**
   - Write unit tests for all services
   - Write integration tests for API endpoints
   - Use pytest for testing
   - Aim for high code coverage

4. **Security Best Practices**
   - Validate all input data
   - Use proper authentication and authorization
   - Implement rate limiting for public endpoints
   - Secure sensitive data and API keys

## Database Migrations

Alembic is used for managing MongoDB schema changes:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

Example migration script:

```python
# app/db/migrations/versions/202503201234_create_indexes.py
"""create_indexes

Revision ID: abcd1234
"""

async def migrate(db):
    """Create indexes for collections."""
    # Create index for downloads
    await db.downloads.create_index("image_id")
    await db.downloads.create_index("timestamp")
    
    # Create index for images
    await db.images.create_index("upload_date")
    await db.images.create_index("download_count")
    
    # Create text index for search
    await db.images.create_index([
        ("title", "text"),
        ("description", "text"),
        ("tags", "text")
    ])
    
    print("Created indexes for collections")
```

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Create a Pull Request

## License

Copyright © 2025 Thirteenk. All rights reserved.
