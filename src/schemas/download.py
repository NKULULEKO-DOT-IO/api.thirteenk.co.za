from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DownloadCreate(BaseModel):
    image_id: str
    ip_address: str
    user_agent: str
    referer: Optional[str] = None
    country_code: Optional[str] = None


class DownloadInDB(DownloadCreate):
    id: str
    timestamp: datetime

    class Config:
        orm_mode = True


class DownloadResponse(BaseModel):
    download_url: str


class DownloadCountResponse(BaseModel):
    total_downloads: int