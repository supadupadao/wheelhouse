from logging import getLogger
from pathlib import Path

from libs.db import Database

logger = getLogger(__name__)


async def run_migrations(db: Database, path: str = "migrations"):
    files = sorted(Path(path).glob("*.sql"))
    for file in files:
        logger.info("Running %s migration", file)
        sql = file.read_text()
        await db.execute(sql)
