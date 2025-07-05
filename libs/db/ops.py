from typing import Optional

from tonsdk.utils import Address

from libs.db import DAO, Database, TraceLog, address_into_db_format, Proposal
from libs.db.models import JettonWallet, DAOParticipant
from libs.db.utils import address_from_db_format


# DAO


async def insert_dao(conn: Database, dao: DAO) -> None:
    await conn.execute(
        """
        INSERT INTO dao (
            address,
            jetton_master,
            jetton_name,
            jetton_symbol,
            jetton_icon_url,
            jetton_description
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (address) DO UPDATE set jetton_master=$2
        """,
        address_into_db_format(dao.address),
        address_into_db_format(dao.jetton_master),
        dao.jetton_name,
        dao.jetton_symbol,
        dao.jetton_icon_url,
        dao.jetton_description,
    )


async def list_dao(conn: Database) -> list[DAO]:
    rows = await conn.fetch_all(
        "SELECT * FROM dao",
    )
    return [
        DAO(
            address=address_from_db_format(r.get("address")),
            jetton_master=address_from_db_format(r.get("jetton_master")),
            jetton_name=r.get("jetton_name"),
            jetton_symbol=r.get("jetton_symbol"),
            jetton_description=r.get("jetton_description"),
            jetton_icon_url=r.get("jetton_icon_url"),
        )
        for r in rows
    ]


async def get_dao(conn: Database, address: Address) -> Optional[DAO]:
    row = await conn.fetch_one(
        """
        SELECT * FROM dao WHERE address=$1
        """,
        address_into_db_format(address),
    )
    if row is not None:
        return DAO(
            address=address_from_db_format(row.get("address")),
            jetton_master=address_from_db_format(row.get("jetton_master")),
            jetton_name=row.get("jetton_name"),
            jetton_symbol=row.get("jetton_symbol"),
            jetton_description=row.get("jetton_description"),
            jetton_icon_url=row.get("jetton_icon_url"),
        )
    return None


# DAO participant


async def insert_dao_participant(conn: Database, participant: DAOParticipant) -> None:
    await conn.execute(
        """
        INSERT INTO dao_participant(dao, address, jetton_wallet, lock_address)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (dao, address)
        DO UPDATE SET jetton_wallet=$3, lock_address=$4
        """,
        address_into_db_format(participant.dao),
        address_into_db_format(participant.address),
        address_into_db_format(participant.jetton_wallet),
        (
            address_into_db_format(participant.lock_address)
            if participant.lock_address
            else None
        ),
    )


async def get_dao_participant(
    conn: Database, dao: Address, address: Address
) -> Optional[DAOParticipant]:
    row = await conn.fetch_one(
        """
        SELECT * FROM dao_participant WHERE dao=$1 AND address=$2
        """,
        address_into_db_format(dao),
        address_into_db_format(address),
    )
    if row is not None:
        lock_address = row.get("lock_address")
        return DAOParticipant(
            dao=address_from_db_format(row.get("dao")),
            address=address_from_db_format(row.get("address")),
            jetton_wallet=address_from_db_format(row.get("jetton_wallet")),
            lock_address=address_from_db_format(lock_address) if lock_address else None,
        )
    return None


# Proposal


async def insert_proposal(conn: Database, proposal: Proposal) -> None:
    await conn.execute(
        """
        INSERT INTO proposal (
            address,
            dao,
            id,
            is_initialized,
            is_executed,
            votes_yes,
            votes_no,
            expires_at,
            receiver,
            payload
        ) VALUES (
            $1,
            $2,
            $3,
            $4,
            $5,
            $6,
            $7,
            $8,
            $9,
            $10
        ) ON CONFLICT (address)
        DO UPDATE SET
            dao=$2,
            id=$3,
            is_initialized=$4,
            is_executed=$5,
            votes_yes=$6,
            votes_no=$7,
            expires_at=$8,
            receiver=$9,
            payload=$10
        """,
        address_into_db_format(proposal.address),
        address_into_db_format(proposal.dao),
        proposal.id,
        proposal.is_initialized,
        proposal.is_executed,
        proposal.votes_yes,
        proposal.votes_no,
        proposal.expires_at,
        address_into_db_format(proposal.receiver),
        proposal.payload,
    )


async def list_proposals(conn: Database, dao: Address) -> list[Proposal]:
    rows = await conn.fetch_all(
        """
        SELECT * FROM proposal WHERE dao = $1
        """,
        address_into_db_format(dao),
    )
    return [
        Proposal(
            address=address_from_db_format(r.get("address")),
            dao=address_from_db_format(r.get("dao")),
            id=r.get("id"),
            is_initialized=r.get("is_initialized"),
            is_executed=r.get("is_executed"),
            votes_yes=r.get("votes_yes"),
            votes_no=r.get("votes_no"),
            expires_at=r.get("expires_at"),
            receiver=address_from_db_format(r.get("receiver")),
            payload=r.get("payload"),
        )
        for r in rows
    ]


async def get_proposal_by_id(
    conn: Database, dao: Address, proposal_id: int
) -> Optional[Proposal]:
    row = await conn.fetch_one(
        """
        SELECT * FROM proposal WHERE dao=$1 AND id=$2
        """,
        address_into_db_format(dao),
        proposal_id,
    )
    if row is not None:
        return Proposal(
            address=address_from_db_format(row.get("address")),
            dao=address_from_db_format(row.get("dao")),
            id=row.get("id"),
            is_initialized=row.get("is_initialized"),
            is_executed=row.get("is_executed"),
            votes_yes=row.get("votes_yes"),
            votes_no=row.get("votes_no"),
            expires_at=row.get("expires_at"),
            receiver=address_from_db_format(row.get("receiver")),
            payload=row.get("payload"),
        )
    return None


# TraceLog


async def insert_trace(conn: Database, trace_log: TraceLog):
    await conn.execute(
        """
        INSERT INTO trace_log (address, hash, utime) VALUES ($1, $2, $3)
        """,
        address_into_db_format(trace_log.address),
        trace_log.hash,
        trace_log.utime,
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


# Jetton Wallet


async def insert_jetton_wallet(conn: Database, jetton_wallet: JettonWallet):
    await conn.execute(
        """
        INSERT INTO jetton_wallet (address, owner, jetton_master, balance) VALUES ($1, $2, $3, $4)
        ON CONFLICT (address, jetton_master)
        DO UPDATE SET
            balance = $4
        """,
        address_into_db_format(jetton_wallet.address),
        address_into_db_format(jetton_wallet.owner),
        address_into_db_format(jetton_wallet.jetton_master),
        jetton_wallet.balance,
    )


async def get_jetton_wallet_by_address(
    conn: Database, address: Address
) -> Optional[JettonWallet]:
    row = await conn.fetch_one(
        """
        SELECT * FROM jetton_wallet WHERE address=$1
        """,
        address_into_db_format(address),
    )
    if row is not None:
        return JettonWallet(
            address=address_from_db_format(row.get("address")),
            owner=address_from_db_format(row.get("owner")),
            jetton_master=address_from_db_format(row.get("jetton_master")),
            balance=row.get("balance"),
        )
    return None


async def get_jetton_wallet_by_owner(
    conn: Database, owner: Address
) -> Optional[JettonWallet]:
    row = await conn.fetch_one(
        """
        SELECT * FROM jetton_wallet WHERE owner=$1
        """,
        address_into_db_format(owner),
    )
    if row is not None:
        return JettonWallet(
            address=address_from_db_format(row.get("address")),
            owner=address_from_db_format(row.get("owner")),
            jetton_master=address_from_db_format(row.get("jetton_master")),
            balance=row.get("balance"),
        )
    return None
