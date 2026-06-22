from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "KnowFlow AI Backend"
    version: str = "0.1.0"
    environment: str = "development"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
