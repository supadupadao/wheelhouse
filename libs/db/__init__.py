from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

import asyncpg

from libs.db.models import DAO, Wallet, Proposal, Vote, TraceLog
from libs.db.utils import address_into_db_format


class Database:
    _dsn: str
    pool: Optional[asyncpg.Pool]

    def __init__(self, dsn: str):
        self._dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self._dsn, min_size=1, max_size=10)

    async def close(self):
        await self.pool.close()

    async def fetch_all(self, sql: str, *args) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)

    async def fetch_one(self, sql: str, *args) -> Optional[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    async def execute(self, sql: str, *args) -> None:
        async with self.pool.acquire() as conn:
            return await conn.execute(sql, *args)

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Используется как:
        async with db.transaction() as conn:
            await conn.execute(...)
            await conn.fetch(...)
        """
        if not self.pool:
            raise RuntimeError("Pool is not initialized")

        conn = await self.pool.acquire()
        try:
            async with conn.transaction():
                yield conn
        finally:
            await self.pool.release(conn)


__all__ = ["Database", "DAO", "Wallet", "Proposal", "Vote", "TraceLog", "address_into_db_format"]
