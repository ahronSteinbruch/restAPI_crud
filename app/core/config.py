# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB_NAME: str

    @computed_field
    @property
    def MONGO_URI(self) -> str:
        """
        Builds the full MongoDB URI from individual components.
        It URL-encodes the username and password for safety.
        """
        encoded_user = quote_plus(self.MONGO_USER)
        encoded_password = quote_plus(self.MONGO_PASSWORD)

        return f"mongodb://{encoded_user}:{encoded_password}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB_NAME}?authSource=admin"

    model_config = SettingsConfigDict(env_file=".env")


# Create a single, importable instance of the settings
settings = Settings()