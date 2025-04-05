from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.image import PyObjectId


class Download(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    image_id: str
    ip_address: str
    user_agent: str
    referer: Optional[str] = None
    country_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }