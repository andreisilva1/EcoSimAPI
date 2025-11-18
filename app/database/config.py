from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", extra="ignore"
)


class DatabaseSettings(BaseSettings):
    model_config = _base_config
    DATABASE_URL: str


database_settings = DatabaseSettings()
