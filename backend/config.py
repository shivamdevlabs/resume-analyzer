"""
config.py — Application settings loaded from environment variables.
Uses pydantic-settings so every variable is validated at startup.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # --- Google Gemini ---
    GEMINI_API_KEY: str = "AIzaSyB1mPk4Est6_7I8cIjqWEcSJAdc_BtRozc"

    # --- MongoDB ---
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DB_NAME: str = "careercraft"

    # --- App ---
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    JWT_SECRET: str = "careercraft_super_secret_key_123456"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), ".env"),
        "extra": "ignore",
    }


# Singleton — import this everywhere
settings = Settings()
