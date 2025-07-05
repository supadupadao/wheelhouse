from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError

from libs.error import IndexerSettingsError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_")

    DB_URL: str = "postgresql://postgres:password@localhost:5432/skipper"


def init_settings() -> Settings:
    try:
        return Settings()
    except SettingsError as err:
        raise IndexerSettingsError(err)
