import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    secret_key: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "temporary-secret-key-for-dev-12345"))
    algorithm: str = os.getenv("JWT_ALGORITHM", os.getenv("ALGORITHM", "HS256"))
    access_token_expire_time: int = int(os.getenv("JWT_EXPIRE_MINUTES", os.getenv("ACCESS_TOKEN_EXPIRE_TIME", "60")))

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()