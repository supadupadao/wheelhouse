from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select, Session
from tonsdk.boc import Cell

from api.app.api.utils import APIAddress
from api.app.db import engine
from api.app.tonapi import tonapi_client, limiter
from libs.db import DAO, address_into_db_format
from libs.db.utils import str_to_address

router = APIRouter(prefix="/get_jetton_master")


class JettonMasterResponse(BaseModel):
    address: APIAddress


@router.get("/", summary="Execute get_jetton_master")
async def get_jetton_master(dao: str) -> JettonMasterResponse:
    dao_address = str_to_address(dao)
    bin_address = address_into_db_format(dao_address)

    # Check is DAO exists
    with Session(engine) as session:
        query = select(DAO).where(DAO.address == bin_address)
        session.exec(query).one()

    async with limiter:
        result = await tonapi_client.blockchain.execute_get_method(
            dao_address.to_string(),
            "get_jetton_master",
        )
    if not result.success:
        raise Exception(result)
    addr = (
        Cell.one_from_boc(bytes.fromhex(result.stack[0].cell))
        .begin_parse()
        .read_msg_addr()
    )

    return JettonMasterResponse(address=APIAddress.from_address(addr))
