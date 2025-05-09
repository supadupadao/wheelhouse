from dataclasses import dataclass

from sqlalchemy import Engine

from indexer.config import Settings


@dataclass
class Context:
    cfg: Settings
    db: Engine
