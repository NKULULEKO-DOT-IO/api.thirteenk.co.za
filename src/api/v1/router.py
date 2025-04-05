from fastapi import APIRouter

from src.api.v1.endpoints import images, downloads

api_router = APIRouter()
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(downloads.router, prefix="/downloads", tags=["downloads"])