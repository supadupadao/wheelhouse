from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError

from libs.error import IndexerSettingsError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="api_")

    is_testnet: bool = True
    log_level: str = "INFO"
    db_url: str = "postgresql://postgres:password@localhost:5432/skipper"


def init_settings() -> Settings:
    try:
        return Settings()
    except SettingsError as err:
        raise IndexerSettingsError(err)
