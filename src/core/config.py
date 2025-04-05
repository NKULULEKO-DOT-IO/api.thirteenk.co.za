from functools import lru_cache
from typing import Dict, Any, Optional
from pydantic import validator, AnyHttpUrl
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # API
    API_VERSION: str
    API_PREFIX: str
    DEBUG: bool
    PROJECT_NAME: str
    SECRET_KEY: str
    APP_VERSION: str

    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    # Google Cloud Storage
    GCS_PROJECT_ID: str
    GCS_ORIGINAL_BUCKET: str
    GCS_THUMBNAIL_BUCKET: str
    GCS_CREDENTIALS_JSON: str

    # Logging
    LOG_LEVEL: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()