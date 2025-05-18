from decimal import Decimal

from sqlalchemy import LargeBinary, BigInteger, Numeric
from sqlmodel import SQLModel, Field


class DAO(SQLModel, table=True):
    address: bytes = Field(primary_key=True, sa_type=LargeBinary)


class Wallet(SQLModel, table=True):
    address: bytes = Field(primary_key=True, sa_type=LargeBinary)


class Proposal(SQLModel, table=True):
    address: bytes = Field(primary_key=True, sa_type=LargeBinary)
    dao: bytes = Field(foreign_key="dao.address", sa_type=LargeBinary)
    id: int = Field()
    is_initialized: bool = Field()
    is_executed: bool = Field()
    votes_yes: Decimal = Field(sa_type=Numeric(39, 0), nullable=False, default=0)
    votes_no: Decimal = Field(sa_type=Numeric(39, 0), nullable=False, default=0)
    expires_at: int = Field()
    # payload


class Vote(SQLModel, table=True):
    proposal: bytes = Field(foreign_key="proposal.address", primary_key=True, sa_type=LargeBinary)
    wallet: bytes = Field(foreign_key="wallet.address", primary_key=True, sa_type=LargeBinary)


class TraceLog(SQLModel, table=True):
    dao: bytes = Field(foreign_key="dao.address", sa_type=LargeBinary)
    hash: str = Field(primary_key=True)
    utime: int = Field(sa_type=BigInteger)
