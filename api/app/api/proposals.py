from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select, Session

from api.app.db import engine
from indexer.app.ton.utils import str_to_address
from libs.db import Proposal, address_into_db_format

router = APIRouter(prefix="/proposals")


class ProposalItem(BaseModel):
    id: int


class ProposalsList(BaseModel):
    proposals: list[ProposalItem]


@router.get("/", summary="List proposals")
async def list_proposals(dao: str) -> ProposalsList:
    dao_address = str_to_address(dao)
    bin_address = address_into_db_format(dao_address)

    with Session(engine) as session:
        query = select(Proposal).where(Proposal.dao == bin_address).order_by(Proposal.id)
        proposals = session.exec(query).all()

    return ProposalsList(
        proposals=[
            ProposalItem(id=proposal.id) for proposal in proposals
        ]
    )
