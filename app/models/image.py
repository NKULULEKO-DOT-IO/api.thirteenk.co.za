from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class Image(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: str
    filename: str
    thumbnail_url: str
    hd_url: str
    file_size: int  # in bytes
    content_type: str  # MIME type
    downloads: int = 0
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_featured: bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }