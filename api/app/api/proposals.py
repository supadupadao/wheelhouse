from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select, Session

from api.app.db import engine
from libs.db import Proposal, address_into_db_format
from libs.db.utils import str_to_address

router = APIRouter(prefix="/proposals")


class ProposalItem(BaseModel):
    id: int
    # address: str  # TODO
    is_initialized: bool
    is_executed: bool
    votes_yes: int
    votes_no: int
    expires_at: int


class ProposalsList(BaseModel):
    proposals: list[ProposalItem]


@router.get("/", summary="List proposals")
async def list_proposals(dao: str) -> ProposalsList:
    dao_address = str_to_address(dao)
    bin_address = address_into_db_format(dao_address)

    with Session(engine) as session:
        query = select(Proposal).where(Proposal.dao == bin_address).order_by(Proposal.id)
        proposals: list[Proposal] = session.exec(query).all()

    return ProposalsList(
        proposals=[
            ProposalItem(
                id=proposal.id,
                is_initialized=proposal.is_initialized,
                is_executed=proposal.is_executed,
                votes_yes=int(proposal.votes_yes),
                votes_no=int(proposal.votes_no),
                expires_at=proposal.expires_at,
            ) for proposal in proposals
        ]
    )
