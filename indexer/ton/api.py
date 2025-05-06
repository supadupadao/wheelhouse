from typing import Optional

from pytonapi import AsyncTonapi
from pytonapi.schema.traces import Trace

from indexer.ton import limiter


async def list_new_traces(
        tonapi_client: AsyncTonapi,
        last_indexed_trace_id: Optional[str],
        dao_address: str,
) -> list[str]:
    all_traces = []
    before_lt = None

    while True:
        async with limiter:
            result = await tonapi_client.accounts.get_traces(dao_address, limit=2, before_lt=before_lt)
        if not len(result.traces):
            break
        for trace in result.traces:
            if trace.id == last_indexed_trace_id:
                return all_traces
            all_traces.append(trace.id)
        before_lt = result.traces[-1].utime

    return all_traces


async def get_trace_info(tonapi_client: AsyncTonapi, trace_id: str) -> Trace:
    return await tonapi_client.traces.get_trace(trace_id)
