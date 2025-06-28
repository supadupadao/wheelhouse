from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.params import Query, Depends
from tonsdk.utils import Address

from api.app.api.utils import APIAddress, get_db
from libs.db import ops, Database

router = APIRouter(prefix="/wallets")


@dataclass
class WalletState:
    address: APIAddress
    balance: int


@dataclass
class WalletInfo:
    address: APIAddress
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
    wallet_address = Address(address)
    dao_address = Address(dao)

    wallet_info = await ops.get_dao_participant(conn, dao_address, wallet_address)
    if not wallet_info:
        raise HTTPException(status_code=404, detail="Wallet not found")

    jetton_info = await ops.get_jetton_wallet(conn, wallet_info.jetton_wallet)
    lock_info = await ops.get_jetton_wallet(conn, wallet_info.lock_address)

    return WalletInfo(
        address=APIAddress.from_address(wallet_address),
        jetton_wallet=WalletState(
            address=APIAddress.from_address(jetton_info.address),
            balance=int(jetton_info.balance),
        ) if jetton_info else None,
        lock=WalletState(
            address=APIAddress.from_address(lock_info.address),
            balance=int(lock_info.balance),
        ) if lock_info else None
    )
