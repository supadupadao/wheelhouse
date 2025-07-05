from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel

from api.app.api.utils import APIAddress, get_db
from libs.db import ops, Database
from libs.db.utils import str_to_address

router = APIRouter(prefix="/dao")


class DAOItem(BaseModel):
    address: APIAddress
    jetton_master: APIAddress
    jetton_name: str
    jetton_symbol: str
    jetton_icon_url: Optional[str]
    jetton_description: Optional[str]


class DAOList(BaseModel):
    dao: list[DAOItem]


@router.get(
    "/",
    tags=["DAO"],
    summary="List DAO",
    description=(
        "Returns a list of all registered DAOs in the system.\n\n"
        "Each DAO entry includes its contract address and associated jetton master"
    ),
)
async def list_dao(conn: Database = Depends(get_db)) -> DAOList:
    dao_list = await ops.list_dao(conn)

    return DAOList(
        dao=[
            DAOItem(
                address=APIAddress.from_address(dao.address),
                jetton_master=APIAddress.from_address(dao.jetton_master),
                jetton_name=dao.jetton_name,
                jetton_symbol=dao.jetton_symbol,
                jetton_description=dao.jetton_description,
                jetton_icon_url=dao.jetton_icon_url,
            )
            for dao in dao_list
        ]
    )


@router.get(
    "/{address}",
    tags=["DAO"],
    summary="Get DAO by address",
    description=(
        "Returns details of a specific DAO by its contract address.\n\n"
        "The response includes the DAO's contract address and associated jetton master."
    ),
)
async def get_dao(address: str, conn: Database = Depends(get_db)) -> DAOItem:
    dao_address = str_to_address(address)
    dao = await ops.get_dao(conn, dao_address)

    if not dao:
        raise HTTPException(status_code=404, detail="DAO not found")

    return DAOItem(
        address=APIAddress.from_address(dao.address),
        jetton_master=APIAddress.from_address(dao.jetton_master),
        jetton_name=dao.jetton_name,
        jetton_symbol=dao.jetton_symbol,
        jetton_description=dao.jetton_description,
        jetton_icon_url=dao.jetton_icon_url,
    )
