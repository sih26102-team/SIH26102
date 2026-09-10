import os
from functools import lru_cache

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    PROJECT_NAME: str = "SIH26102 - MPLAD Scheme Anomaly Detector API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test_data.db",
    )

    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL") or os.getenv("ML_ENGINE_URL") or "http://localhost:8003"
    ML_SERVICE_TIMEOUT_SECONDS: float = float(os.getenv("ML_SERVICE_TIMEOUT_SECONDS", "10"))

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "temporary-secret-key-for-dev-12345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    ENV: str = os.getenv("ENV", "development")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
