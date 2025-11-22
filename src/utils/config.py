from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    DATABASE_URL: str 
    base_url:str
    redis_url: str
    jwt_secret_key:str
    jwt_algo:str 
    access_token_expiry:int
    refresh_token_expiry:int
    # frontend_url:str
    celery_beat_interval:int
    #super super admin details for dspace 
    base_username:str
    base_password:str

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",  # Adjusted to point to the root directory
        env_file_encoding="utf-8",
    )

config = Config()

class Settings:
    PROJECT_NAME: str = "Unical Insitutional Repository"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Backend for Unical Insitutional Repository"
    API_PREFIX: str = "/api/v1"
