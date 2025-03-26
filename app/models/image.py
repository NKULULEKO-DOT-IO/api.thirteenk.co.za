from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field, BeforeValidator
from bson import ObjectId


# Modern Pydantic v2 approach
def validate_object_id(v):
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return str(v)


PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]


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
        populate_by_name = True  # new in v2 (replaces allow_population_by_field_name)
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }