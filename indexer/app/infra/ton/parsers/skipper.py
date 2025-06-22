import logging
from dataclasses import dataclass
from decimal import Decimal
from email.headerregistry import Address
from typing import Optional

from pytonapi import AsyncTonapi
from pytonapi.schema.traces import Trace
from tonsdk.boc import Cell, Slice

from indexer.app.infra.ton import limiter
from indexer.app.infra.ton.parsers import traverse_children, BaseState, S
from libs.error import TonApiError, IndexerDataIsNotReady

logger = logging.getLogger(__name__)


@dataclass
class ProposalData:
    proposal_id: int
    is_initialized: bool
    is_executed: bool
    votes_yes: Decimal
    votes_no: Decimal
    expires_at: int


@dataclass()
class SkipperState(BaseState):
    skipper_address: Address


@dataclass
class NewProposalState(SkipperState):
    address: Address
    proposal_data: ProposalData


@dataclass
class VoteProposalState(SkipperState):
    # TODO FIXME: add votes_yes and votes_no fields
    address: Address
    proposal_data: ProposalData


async def parse_skipper_trace(
        skipper_address: Address, tonapi_client: AsyncTonapi, trace_info: Trace
):
    state = SkipperState(skipper_address=skipper_address, tonapi_client=tonapi_client)

    return await traverse_children(state, trace_info.children or [], find_skipper)


async def find_skipper(state: S, trace: Trace) -> Optional[S]:
    if len(trace.transaction.out_msgs) > 0:
        raise IndexerDataIsNotReady("Skipper transaction is not executed yet")

    account_address = trace.transaction.account.address.to_raw()
    if account_address == state.skipper_address:
        msg_body = trace.transaction.in_msg.raw_body
        cell: Cell = Cell.one_from_boc(msg_body)
        s: Slice = cell.begin_parse()
        opcode = s.read_uint(32)
        if opcode == 0x690102:
            # TODO FIXME
            owner = s.read_msg_addr()
            if s.read_bit():
                lock_period = s.read_uint(64)
            voter_unlock_date = s.read_uint(64)
            amount = s.read_coins()
            # TODO FIXME

            payload = s.read_ref()
            payload_parser = payload.begin_parse()
            proxy_opcode = payload_parser.read_uint(32)

            if proxy_opcode == 0x690401:
                return await traverse_children(
                    state, trace.children, handle_new_proposal
                )
            if proxy_opcode == 0x690402:
                return await traverse_children(
                    state, trace.children, handle_vote_proposal
                )

    if trace.children is not None:
        logger.info("Parsing children")
        return await traverse_children(state, trace.children, find_skipper)
    return None


async def fetch_proposal_state(
        state: S, proposal_contract: str
) -> ProposalData:
    async with limiter:
        result = await state.tonapi_client.blockchain.execute_get_method(
            proposal_contract, "get_proposal_data"
        )
    if result.success:
        proposal_id = int(result.stack[0].num, 16)
        is_initialized = bool(int(result.stack[1].num, 16))
        is_executed = bool(int(result.stack[2].num, 16))
        votes_yes = int(result.stack[3].num, 16)
        votes_no = int(result.stack[4].num, 16)
        expires_at = int(result.stack[5].num, 16)

        return ProposalData(
            proposal_id=proposal_id,
            is_initialized=is_initialized,
            is_executed=is_executed,
            votes_yes=Decimal(votes_yes),
            votes_no=Decimal(votes_no),
            expires_at=expires_at,
        )
    else:
        raise TonApiError("Error fetching proposal state")


async def handle_new_proposal(state: S, trace: Trace) -> Optional[S]:
    if len(trace.transaction.out_msgs) > 0:
        raise IndexerDataIsNotReady("Skipper transaction is not executed yet")

    opcode = int(trace.transaction.in_msg.op_code, 16)
    if opcode == 0x690201:
        proposal_contract = trace.transaction.account.address.to_raw()
        proposal_data = await fetch_proposal_state(state, proposal_contract)
        return NewProposalState(
            skipper_address=state.skipper_address,
            tonapi_client=state.tonapi_client,
            address=Address(proposal_contract),
            proposal_data=proposal_data,
        )
    return await traverse_children(state, trace.children, handle_new_proposal)


async def handle_vote_proposal(state: S, trace: Trace) -> Optional[S]:
    if len(trace.transaction.out_msgs) > 0:
        raise IndexerDataIsNotReady("Skipper transaction is not executed yet")

    opcode = int(trace.transaction.in_msg.op_code, 16)
    if opcode == 0x690202:
        proposal_contract = trace.transaction.account.address.to_raw()
        proposal_data = await fetch_proposal_state(state, proposal_contract)
        return VoteProposalState(
            skipper_address=state.skipper_address,
            tonapi_client=state.tonapi_client,
            address=Address(proposal_contract),
            proposal_data=proposal_data,
        )
    return await traverse_children(state, trace.children, handle_vote_proposal)
