# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


# Create a single, importable instance of the settings
settings = Settings()