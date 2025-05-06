from dataclasses import dataclass
from typing import Optional, Callable

from pytonapi.schema.traces import Trace


@dataclass
class BaseState:
    skipper_address: str


@dataclass
class ProposalPayload:
    receiver: str
    body: str


@dataclass
class ProposalData:
    proposal_id: int
    is_initialized: bool
    is_executed: bool
    votes_yes: int
    votes_no: int
    expires_at: int
    payload: ProposalPayload


@dataclass
class NewProposalState(BaseState):
    initiator: str
    proposal_data: ProposalData


@dataclass
class VoteProposalState(BaseState):
    voter: str
    proposal_id: int
    vote: bool
    amount: int


HandlerFunc = Callable[[BaseState, Trace], Optional[BaseState]]


def parse_trace(raw_skipper_address: str, trace_info: Trace):
    state = BaseState(skipper_address=raw_skipper_address)

    return traverse_children(state, trace_info.children or [], find_skipper)


def find_skipper(state: BaseState, trace: Trace) -> Optional[BaseState]:
    account_address = trace.transaction.account.address.to_raw()
    if account_address == state.skipper_address:
        msg_body = trace.transaction.in_msg.raw_body
        pass  # TODO: parse skipper

    return None


def traverse_children(state: BaseState, children: list[Trace], func: HandlerFunc) -> Optional[BaseState]:
    for child in children:
        new_state = func(state, child)
        if new_state is not None:
            return new_state
    return None
