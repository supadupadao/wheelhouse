from dataclasses import dataclass
from typing import Optional, Callable, Awaitable, TypeVar

from pytonapi import AsyncTonapi
from pytonapi.schema.traces import Trace

from libs.error import IndexerDataIsNotReady


@dataclass
class BaseState:
    tonapi_client: AsyncTonapi


S = TypeVar("S", bound=BaseState)

HandlerFunc = Callable[[S, Trace], Awaitable[Optional[S]]]


async def check_children_success(state: S, trace: Trace) -> Optional[S]:
    if len(trace.transaction.out_msgs) > 0:
        raise IndexerDataIsNotReady("Skipper transaction is not executed yet")
    if not trace.transaction.success:
        return None
    await traverse_children(state, trace.children, check_children_success)

    return state


async def traverse_children(
        state: S, children: list[Trace], func: HandlerFunc
) -> Optional[S]:
    if not children:
        return None
    for child in children:
        new_state = await func(state, child)
        if new_state is not None:
            return new_state
    return None
