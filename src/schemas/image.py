from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ImageBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False


class ImageCreate(ImageBase):
    pass


class ImageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None


class ImageInDB(ImageBase):
    id: str
    filename: str
    thumbnail_url: str
    hd_url: str
    file_size: int
    content_type: str
    downloads: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ImageResponse(ImageInDB):
    pass


class ImagesResponse(BaseModel):
    images: List[ImageResponse]
    total: int