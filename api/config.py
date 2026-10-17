"""
Configuration settings for FloodSentinel FastAPI backend.
"""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "FloodSentinel API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")

    # CORS configuration - default to standard frontend development ports
    cors_origins: List[str] = (
        os.getenv("CORS_ORIGINS", "").split(",")
        if os.getenv("CORS_ORIGINS")
        else [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )

    # Repository paths (relative to base dir)
    base_dir: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../")
    )


settings = Settings()
