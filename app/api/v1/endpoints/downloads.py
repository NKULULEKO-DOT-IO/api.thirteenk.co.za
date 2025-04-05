from fastapi import APIRouter, Depends, Request

from app.api.deps import get_download_service, get_image_service
from app.schemas.download import DownloadResponse, DownloadCountResponse
from app.services.download_service import DownloadService
from app.services.image_service import ImageService
from app.core.logging import logger

router = APIRouter()


@router.post("/{image_id}", response_model=DownloadResponse)
async def download_image(
        image_id: str,
        request: Request,
        download_service: DownloadService = Depends(get_download_service),
        image_service: ImageService = Depends(get_image_service)
):
    """Record a download and return the download URL."""
    logger.info(f"Processing download for image {image_id}")

    # Check if image exists
    image = await image_service.get_image(image_id)

    # Extract request information
    request_info = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", "unknown"),
        "referer": request.headers.get("referer"),
        # Country code would be determined by IP geolocation in production
    }

    # Record the download
    await download_service.record_download(image_id, request_info)

    # Return download URL
    return {"download_url": image.hd_url}


@router.get("/total", response_model=DownloadCountResponse)
async def get_total_downloads(
        download_service: DownloadService = Depends(get_download_service)
):
    """Get the total number of downloads across all images."""
    logger.info("Getting total downloads")
    total = await download_service.get_total_downloads()
    return {"total_downloads": total}


@router.get("/{image_id}/count", response_model=DownloadCountResponse)
async def get_image_downloads(
        image_id: str,
        download_service: DownloadService = Depends(get_download_service),
        image_service: ImageService = Depends(get_image_service)
):
    """Get download count for a specific image."""
    logger.info(f"Getting download count for image {image_id}")

    # Check if image exists
    await image_service.get_image(image_id)

    # Get download count
    total = await download_service.get_image_downloads(image_id)

    return {"total_downloads": total}