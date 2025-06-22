from typing import Optional

from pytonapi import AsyncTonapi
from pytonapi.schema.traces import Trace
from tonsdk.utils import Address

from indexer.app.infra.ton import limiter
from libs.db import TraceLog

MAX_TRACES_PER_PAGE: int = 100


async def list_new_traces(
        tonapi_client: AsyncTonapi,
        last_indexed_trace: Optional[TraceLog],
        address: Address,
) -> list[str]:
    all_traces = []
    before_lt = None

    while True:
        async with limiter:
            result = await tonapi_client.accounts.get_traces(
                address.to_string(),
                limit=MAX_TRACES_PER_PAGE,
                before_lt=before_lt
            )
        if not len(result.traces):
            break
        for trace in result.traces:
            if last_indexed_trace and trace.id == last_indexed_trace.hash:
                return all_traces
            all_traces.append(trace.id)
        before_lt = result.traces[-1].utime

    all_traces.reverse()
    return all_traces


async def get_trace_info(tonapi_client: AsyncTonapi, trace_id: str) -> Trace:
    async with limiter:
        return await tonapi_client.traces.get_trace(trace_id)
