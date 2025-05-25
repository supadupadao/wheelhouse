from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select, Session

from api.app.api.utils import APIAddress
from api.app.db import engine
from libs.db import DAO

router = APIRouter(prefix="/dao")


class DAOItem(BaseModel):
    address: APIAddress


class DAOList(BaseModel):
    dao: list[DAOItem]


@router.get("/", summary="List DAO")
async def list_dao() -> DAOList:
    with Session(engine) as session:
        query = select(DAO)
        dao_list = session.exec(query).all()

    return DAOList(
        dao=[
            DAOItem(
                address=APIAddress.parse_hash_part(dao.address)
            ) for dao in dao_list
        ]
    )
