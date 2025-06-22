from dataclasses import dataclass
from decimal import Decimal

from tonsdk.utils import Address


@dataclass
class DAO:
    address: Address
    jetton_master: Address


@dataclass
class Wallet:
    address: bytes


@dataclass
class JettonWallet:
    jetton_master: bytes
    wallet: bytes
    balance: Decimal


@dataclass
class Proposal:
    address: Address
    dao: Address
    id: int
    is_initialized: bool
    is_executed: bool
    votes_yes: Decimal
    votes_no: Decimal
    expires_at: int


@dataclass
class Vote:
    proposal: bytes
    wallet: bytes


@dataclass
class TraceLog:
    address: Address
    hash: str
    utime: int
