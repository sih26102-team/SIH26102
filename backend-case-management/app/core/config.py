from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    secret_key: str = "temporary-secret-key-for-dev-12345"
    algorithm: str = "HS256"
    access_token_expire_time: int = 60

    class Config:
        env_file = ".env"

settings = Settings()