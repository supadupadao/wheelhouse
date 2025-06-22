from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel

from api.app.api.utils import APIAddress, get_db
from libs.db import ops, Database

router = APIRouter(prefix="/dao")


class DAOItem(BaseModel):
    address: APIAddress


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
                address=APIAddress.from_address(dao.address)
            ) for dao in dao_list
        ]
    )
