from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError

from libs.error import IndexerSettingsError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INDEXER_")

    IS_TESTNET: bool = True
    LOG_LEVEL: str = "INFO"
    DB_URL: str = "postgresql://postgres:password@localhost:5432/skipper"
    SKIPPER_MINTER_ADDRESS: str = "EQ..."
    TONAPI_TOKEN: Optional[str] = None


def init_settings() -> Settings:
    try:
        return Settings()
    except SettingsError as err:
        raise IndexerSettingsError(err)
