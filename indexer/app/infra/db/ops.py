from typing import Optional

from tonsdk.utils import Address

from libs.db import DAO, Database, TraceLog, address_into_db_format, Proposal
from libs.db.utils import address_from_db_format


# DAO


async def insert_dao(conn: Database, dao: DAO):
    await conn.execute(
        """
        INSERT INTO dao (address, jetton_master) VALUES ($1, $2)
        ON CONFLICT (address) DO UPDATE set jetton_master=$2
        """,
        address_into_db_format(dao.address),
        address_into_db_format(dao.jetton_master),
    )


async def list_dao(conn: Database) -> list[DAO]:
    rows = await conn.fetch_all(
        "SELECT * FROM dao",
    )
    return [DAO(
        address=address_from_db_format(r.get("address")),
        jetton_master=address_from_db_format(r.get("jetton_master")),
    ) for r in rows]


# Proposal

async def insert_proposal(conn: Database, proposal: Proposal):
    await conn.execute(
        """
        INSERT INTO proposals (
            address,
            dao,
            id,
            is_initialized,
            is_executed,
            votes_yes,
            votes_no,
            expires_at,
        ) VALUES (
            $1,
            $2,
            $3,
            $4,
            $5,
            $6,
            $7,
            $8,
        ) ON CONFLICT (address)
        DO UPDATE
            dao=$2,
            id=$3,
            is_initialized=$4,
            is_executed=$5,
            votes_yes=$6,
            votes_no=$7,
            expires_at=$8,
        """
    )


# TraceLog


async def insert_trace(conn: Database, trace_log: TraceLog):
    await conn.execute(
        """
        INSERT INTO trace_log (address, hash, utime) VALUES ($1, $2, $3)
        """,
        address_into_db_format(trace_log.address),
        trace_log.hash,
        trace_log.utime
    )


async def get_last_trace(conn: Database, address: Address) -> Optional[TraceLog]:
    row = await conn.fetch_one(
        """
        SELECT address, hash, utime FROM trace_log WHERE address=$1 ORDER BY utime DESC
        """,
        address_into_db_format(address),
    )
    if row is not None:
        return TraceLog(**row)
    return None
