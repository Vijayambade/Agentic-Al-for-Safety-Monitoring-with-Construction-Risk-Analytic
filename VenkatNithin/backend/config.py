"""
backend/config.py
-----------------
Centralised settings loader for the Construction Intelligent Hub.

All configuration is read from environment variables (with sensible defaults)
and, when present, from the `.env` file located at the project root.

Usage
-----
    from backend.config import settings          # use the module-level singleton
    from backend.config import get_settings      # use the factory (e.g. FastAPI DI)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Values are loaded (in priority order) from:
    1. Actual environment variables
    2. The `.env` file at the project root
    3. The default values declared below
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    environment: str = "development"
    app_name: str = "Construction Intelligent Hub"
    app_version: str = "1.0.0"
    secret_key: str = "change-me"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str = "sqlite:///./data/construction_hub.db"
    mongo_uri: str = "mongodb://localhost:27017/construction_hub"
    redis_url: str = "redis://localhost:6379/0"

    # ------------------------------------------------------------------
    # JWT Authentication
    # ------------------------------------------------------------------
    jwt_secret: str = "change-me-jwt"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440
    jwt_remember_me_expire_days: int = 30

    # ------------------------------------------------------------------
    # AI Services
    # ------------------------------------------------------------------
    gemini_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    llm_provider: str = "local"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ------------------------------------------------------------------
    # Embedding Model
    # ------------------------------------------------------------------
    embedding_model: str = "all-MiniLM-L6-v2"

    # ------------------------------------------------------------------
    # Google Maps
    # ------------------------------------------------------------------
    google_maps_api_key: str = ""

    # ------------------------------------------------------------------
    # Weather API (OpenWeatherMap)
    # ------------------------------------------------------------------
    weather_api_key: str = ""
    weather_api_url: str = "https://api.openweathermap.org/data/2.5"

    # ------------------------------------------------------------------
    # Email (SMTP)
    # ------------------------------------------------------------------
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from_name: str = "Construction Intelligent Hub"
    smtp_tls: bool = True

    # ------------------------------------------------------------------
    # SMS Gateway
    # ------------------------------------------------------------------
    sms_gateway_key: str = ""
    sms_gateway_url: str = ""

    # ------------------------------------------------------------------
    # Encryption
    # ------------------------------------------------------------------
    encryption_key: str = ""

    # ------------------------------------------------------------------
    # File Storage
    # ------------------------------------------------------------------
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50
    faiss_index_dir: str = "./data/faiss_indexes"
    yolo_weights_path: str = "./ai/models/yolo_weights/yolov8n.pt"

    # ------------------------------------------------------------------
    # OCR
    # ------------------------------------------------------------------
    tesseract_cmd: str = "/usr/bin/tesseract"

    # ------------------------------------------------------------------
    # Frontend / Server
    # ------------------------------------------------------------------
    backend_url: str = "http://localhost:8000"
    streamlit_server_port: int = 8501

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = "INFO"
    log_dir: str = "./logs"

    # ------------------------------------------------------------------
    # Rate Limiting
    # ------------------------------------------------------------------
    rate_limit_login_max: int = 5
    rate_limit_lockout_minutes: int = 30

    # ------------------------------------------------------------------
    # Cache TTLs (seconds)
    # ------------------------------------------------------------------
    cache_ttl_seconds: int = 3600
    weather_cache_ttl_seconds: int = 1800
    analytics_cache_ttl_seconds: int = 60

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        """Return ``True`` when the app is running in the production environment."""
        return self.environment.lower() == "production"


# ---------------------------------------------------------------------------
# Module-level singleton — import this directly for simple access.
# ---------------------------------------------------------------------------
settings = Settings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached ``Settings`` singleton.

    Designed for use with FastAPI's dependency injection system::

        from fastapi import Depends
        from backend.config import get_settings, Settings

        @router.get("/info")
        def info(cfg: Settings = Depends(get_settings)):
            return {"app": cfg.app_name, "version": cfg.app_version}
    """
    return settings
