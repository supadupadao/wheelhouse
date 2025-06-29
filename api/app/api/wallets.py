from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter
from fastapi.params import Query, Depends

from api.app.api.utils import APIAddress, get_db
from libs.db import ops, Database
from libs.db.utils import str_to_address

router = APIRouter(prefix="/wallets")


@dataclass
class WalletState:
    address: APIAddress
    balance: int


@dataclass
class WalletInfo:
    address: APIAddress
    is_participant: bool
    jetton_wallet: Optional[WalletState]
    lock: Optional[WalletState]


@router.get(
    "/{address}",
    tags=["User"],
    summary="Get wallet information by address",
    description=(
            "Retrieves detailed information about a specific wallet, including its jetton wallet address, "
            "jetton balance, lock address, and lock balance. "
            "Requires the TON address of the DAO as a query parameter."
    ),
)
async def list_dao(
        address: str,
        dao: str = Query(..., description="TON Address of the DAO"),
        conn: Database = Depends(get_db),
) -> WalletInfo:
    wallet_address = str_to_address(address)
    dao_address = str_to_address(dao)

    wallet_info = await ops.get_dao_participant(conn, dao_address, wallet_address)
    if not wallet_info:
        return WalletInfo(
            address=APIAddress.from_address(wallet_address),
            is_participant=wallet_info is not None,
            jetton_wallet=None,
            lock=None,
        )

    jetton_info = await ops.get_jetton_wallet_by_address(conn, wallet_info.jetton_wallet)
    lock_info = await ops.get_jetton_wallet_by_owner(conn, wallet_info.lock_address)

    return WalletInfo(
        address=APIAddress.from_address(wallet_address),
        is_participant=wallet_info is not None,
        jetton_wallet=WalletState(
            address=APIAddress.from_address(wallet_info.jetton_wallet),
            balance=int(jetton_info.balance) if jetton_info else 0,
        ),
        lock=WalletState(
            address=APIAddress.from_address(wallet_info.lock_address),
            balance=int(lock_info.balance) if lock_info else 0,
        ),
    )
