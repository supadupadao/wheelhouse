from fastapi import APIRouter
from fastapi import HTTPException
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
    receiver: APIAddress
    payload: str


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
                receiver=APIAddress.from_address(proposal.receiver),
                payload=proposal.payload,
            )
            for proposal in proposals
        ]
    )


@router.get(
    "/{proposal_id}",
    summary="Get proposal info",
    tags=["Proposals"],
    description="Returns information about a single proposal by its ID.",
    response_model=ProposalItem,
)
async def get_proposal(
    proposal_id: int,
    dao: str = Query(..., description="TON Address of the DAO"),
    conn: Database = Depends(get_db),
) -> ProposalItem:
    dao_address = str_to_address(dao)
    proposal = await ops.get_proposal_by_id(conn, dao_address, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return ProposalItem(
        id=proposal.id,
        address=APIAddress.from_address(proposal.address),
        is_initialized=proposal.is_initialized,
        is_executed=proposal.is_executed,
        votes_yes=int(proposal.votes_yes),
        votes_no=int(proposal.votes_no),
        expires_at=proposal.expires_at,
        receiver=APIAddress.from_address(proposal.receiver),
        payload=proposal.payload,
    )
