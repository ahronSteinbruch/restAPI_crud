# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "mydatabase"

    # This tells Pydantic to look for a .env file if variables are not in the environment
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create a single, importable instance of the settings
settings = Settings()
