from dataclasses import dataclass

from pytonapi import AsyncTonapi

from indexer.app.config import Settings
from libs.db import Database


@dataclass
class Context:
    cfg: Settings
    db: Database
    tonapi_client: AsyncTonapi
