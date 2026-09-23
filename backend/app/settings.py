import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = os.getenv('ENV_FILE', '.env')

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str

    model_config = SettingsConfigDict(env_file=ENV_FILE)

settings = Settings()