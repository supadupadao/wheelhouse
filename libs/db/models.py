from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from tonsdk.utils import Address


@dataclass
class DAO:
    address: Address
    jetton_master: Address
    jetton_name: str
    jetton_symbol: str
    jetton_icon_url: Optional[str]
    jetton_description: Optional[str]


@dataclass
class DAOParticipant:
    dao: Address
    address: Address
    jetton_wallet: Address
    lock_address: Optional[Address]


@dataclass
class Wallet:
    address: bytes


@dataclass
class JettonWallet:
    address: Address
    owner: Address
    jetton_master: Address
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
    receiver: Address
    payload: str


@dataclass
class Vote:
    proposal: bytes
    wallet: bytes


@dataclass
class TraceLog:
    address: Address
    hash: str
    utime: int
