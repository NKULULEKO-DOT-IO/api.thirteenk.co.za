from typing import Generator

from fastapi import Depends

from src.services.image_service import ImageService
from src.services.download_service import DownloadService
from src.services.storage_service import StorageService


def get_image_service() -> ImageService:
    """Dependency to get image service."""
    return ImageService()


def get_download_service() -> DownloadService:
    """Dependency to get download service."""
    return DownloadService()


def get_storage_service() -> StorageService:
    """Dependency to get storage service."""
    return StorageService()