import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017/timelysync"
    internal_api_key: str = ""
    models_dir: str = str(BASE_DIR / "models")
    port: int = 8000
    cors_allowed_origins: str = "http://localhost:8080,http://localhost:3000"
    log_level: str = "INFO"


settings = Settings(
    mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017/timelysync"),
    internal_api_key=os.getenv("AI_INTERNAL_API_KEY", ""),
    models_dir=os.getenv("MODELS_DIR", str(BASE_DIR / "models")),
    port=int(os.getenv("PORT", "8000")),
    cors_allowed_origins=os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:3000"),
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)
