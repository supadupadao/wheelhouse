from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError

from indexer.error import IndexerSettingsError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="indexer_")

    is_testnet: bool = True
    log_level: str = "INFO"
    db_url: str = "postgresql://postgres:password@localhost:5432/skipper"
    skipper_address: str = "EQ..."
    tonapi_token: Optional[str] = None


def init_settings() -> Settings:
    try:
        return Settings()
    except SettingsError as err:
        raise IndexerSettingsError(err)
