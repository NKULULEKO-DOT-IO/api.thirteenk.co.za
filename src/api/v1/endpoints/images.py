from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.api.deps import get_image_service
from src.schemas.image import ImageCreate, ImageUpdate, ImageResponse, ImagesResponse
from src.services.image_service import ImageService
from src.core.logging import logger

router = APIRouter()


@router.get("/", response_model=ImagesResponse)
async def get_images(
        skip: int = 0,
        limit: int = 20,
        tags: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        image_service: ImageService = Depends(get_image_service)
):
    """Get a list of images with optional filtering."""
    logger.info(f"Getting images with skip={skip}, limit={limit}, tags={tags}, featured={featured}")
    images = await image_service.get_images(skip, limit, tags, featured)
    total_count = await image_service.count_images(tags, featured)
    return {"images": images, "total": total_count}


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
        image_id: str,
        image_service: ImageService = Depends(get_image_service)
):
    """Get a single image by ID."""
    logger.info(f"Getting image with ID {image_id}")
    image = await image_service.get_image(image_id)
    return image


@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
        name: str = Form(...),
        description: Optional[str] = Form(None),
        tags: Optional[str] = Form(None),
        is_featured: Optional[bool] = Form(False),
        file: UploadFile = File(...),
        image_service: ImageService = Depends(get_image_service)
):
    """Upload a new image."""
    logger.info(f"Creating new image: {name}")

    # Process form data
    tags_list = tags.split(",") if tags else []
    image_data = {
        "name": name,
        "description": description or "",
        "tags": tags_list,
        "is_featured": is_featured
    }

    return await image_service.create_image(file, image_data)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
        image_id: str,
        image_service: ImageService = Depends(get_image_service)
):
    """Delete an image."""
    logger.info(f"Deleting image with ID {image_id}")
    await image_service.delete_image(image_id)
    return None