import logging
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable

from pytonapi import AsyncTonapi
from pytonapi.schema.traces import Trace
from tonsdk.boc import Cell, Slice

from indexer.ton import limiter


@dataclass
class BaseState:
    skipper_address: str
    tonapi_client: AsyncTonapi


@dataclass
class ProposalData:
    proposal_id: int
    is_initialized: bool
    is_executed: bool
    votes_yes: int
    votes_no: int
    expires_at: int


@dataclass
class NewProposalState(BaseState):
    proposal_data: ProposalData


@dataclass
class VoteProposalState(BaseState):
    voter: str
    proposal_id: int
    vote: bool
    amount: int


HandlerFunc = Callable[[BaseState, Trace], Awaitable[Optional[BaseState]]]


async def parse_trace(raw_skipper_address: str, tonapi_client: AsyncTonapi, trace_info: Trace):
    state = BaseState(skipper_address=raw_skipper_address, tonapi_client=tonapi_client)

    return await traverse_children(state, trace_info.children or [], find_skipper)


async def find_skipper(state: BaseState, trace: Trace) -> Optional[BaseState]:
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
                return await traverse_children(state, trace.children, handle_new_proposal)
            if proxy_opcode == 0x690402:
                return await traverse_children(state, trace.children, handle_vote_proposal)

    if trace.children is not None:
        logging.info("Parsing children")
        return await traverse_children(state, trace.children, find_skipper)
    return None


async def handle_new_proposal(state: BaseState, trace: Trace) -> Optional[BaseState]:
    opcode = int(trace.transaction.in_msg.op_code, 16)
    if opcode == 0x690201:
        proposal_contract = trace.transaction.account.address.to_raw()
        async with limiter:
            result = await state.tonapi_client.blockchain.execute_get_method(proposal_contract,
                                                                             "get_proposal_data")
            if result.success:
                proposal_id = int(result.stack[0].num, 16)
                is_initialized = bool(int(result.stack[1].num, 16))
                is_executed = bool(int(result.stack[2].num, 16))
                votes_yes = int(result.stack[3].num, 16)
                votes_no = int(result.stack[4].num, 16)
                expires_at = int(result.stack[5].num, 16)

                return NewProposalState(
                    skipper_address=state.skipper_address,
                    tonapi_client=state.tonapi_client,

                    proposal_data=ProposalData(
                        proposal_id=proposal_id,
                        is_initialized=is_initialized,
                        is_executed=is_executed,
                        votes_yes=votes_yes,
                        votes_no=votes_no,
                        expires_at=expires_at,
                    )
                )
    return await traverse_children(state, trace.children, handle_new_proposal)


async def handle_vote_proposal(state: BaseState, trace: Trace) -> Optional[BaseState]:
    print("VOTE PROPOSAL HANDLER")  # TODO
    return None


async def traverse_children(state: BaseState, children: list[Trace], func: HandlerFunc) -> Optional[BaseState]:
    if not children:
        return None
    for child in children:
        new_state = await func(state, child)
        if new_state is not None:
            return new_state
    return None
