from fastapi import APIRouter
from fastapi.params import Depends, Query
from pydantic import BaseModel

from api.app.api.utils import APIAddress, get_db
from libs.db import Database, ops
from libs.db.utils import str_to_address

router = APIRouter(prefix="/proposals")


class ProposalItem(BaseModel):
    id: int
    address: APIAddress
    is_initialized: bool
    is_executed: bool
    votes_yes: int
    votes_no: int
    expires_at: int


class ProposalsList(BaseModel):
    proposals: list[ProposalItem]


@router.get(
    "/",
    summary="List proposals",
    tags=["Proposals"],
    description=(
            "Returns a list of proposals for the specified DAO.\n\n"
            "Each proposal includes its status (initialized, executed), vote counts, expiration timestamp"
    ),
)
async def list_proposals(
        dao: str = Query(..., description="TON Address of the DAO"),
        conn: Database = Depends(get_db),
) -> ProposalsList:
    dao_address = str_to_address(dao)
    proposals = await ops.list_proposals(conn, dao_address)
    return ProposalsList(
        proposals=[
            ProposalItem(
                id=proposal.id,
                address=APIAddress.from_address(proposal.address),
                is_initialized=proposal.is_initialized,
                is_executed=proposal.is_executed,
                votes_yes=int(proposal.votes_yes),
                votes_no=int(proposal.votes_no),
                expires_at=proposal.expires_at,
            ) for proposal in proposals
        ]
    )
