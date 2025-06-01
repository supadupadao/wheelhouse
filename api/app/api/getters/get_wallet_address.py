from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select, Session
from tonsdk.boc import Cell, begin_cell

from api.app.api.utils import APIAddress
from api.app.db import engine
from api.app.tonapi import tonapi_client
from libs.db import DAO, address_into_db_format
from libs.db.utils import str_to_address

router = APIRouter(prefix="/get_wallet_address")


class LockAddressResult(BaseModel):
    address: APIAddress


@router.get("/", summary="Execute get_wallet_address")
async def list_dao(dao: str, owner: str) -> LockAddressResult:
    dao_address = str_to_address(dao)
    owner_address = str_to_address(owner)
    bin_address = address_into_db_format(dao_address)

    # Check is DAO exists
    with Session(engine) as session:
        query = select(DAO).where(DAO.address == bin_address)
        session.exec(query).one()

    result = await tonapi_client.blockchain.execute_get_method(
        dao_address.to_string(),
        "get_jetton_master",
    )
    if not result.success:
        raise Exception(result)
    addr = Cell.one_from_boc(bytes.fromhex(result.stack[0].cell)).begin_parse().read_msg_addr()

    cell = begin_cell().store_address(owner_address).end_cell()
    result = await tonapi_client.blockchain.execute_get_method(
        addr.to_string(),
        "get_wallet_address",
        cell.to_boc().hex()
    )
    if not result.success:
        raise Exception(result)
    addr = Cell.one_from_boc(bytes.fromhex(result.stack[0].cell)).begin_parse().read_msg_addr()

    return LockAddressResult(
        address=APIAddress.from_address(addr)
    )
