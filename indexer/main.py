import uvloop
from aiolimiter import AsyncLimiter
from pytonapi import Tonapi

from indexer.common.ctx import Context
from indexer.config import init_settings
from indexer.db import init_db, TraceLog
from indexer.db.ops import get_or_create_dao, get_last_trace, insert_trace
from indexer.db.utils import address_into_db_format
from indexer.error import BaseIndexerException
from indexer.ton.utils import str_to_address

limiter = AsyncLimiter(max_rate=1, time_period=1.0)


async def main(context: Context):
    tonapi_client = Tonapi(context.cfg.tonapi_token, is_testnet=context.cfg.is_testnet)

    dao_address = str_to_address(context.cfg.skipper_address)
    dao_record = get_or_create_dao(context.db, dao_address)

    while True:
        next_trace_record = get_last_trace(context.db, dao_record)
        async with limiter:
            result = tonapi_client.accounts.get_traces(dao_address.to_string())
        for trace in result.traces:
            trace_log = TraceLog(
                dao=address_into_db_format(dao_address),
                hash=trace.id,
                utime=trace.utime,
            )
            insert_trace(context.db, trace_log)
            print("INSERTED TRACE LOG", trace.id)


if __name__ == "__main__":
    # Initialize config
    try:
        settings = init_settings()
        db = init_db(settings.db_url)
    except BaseIndexerException as err:
        print("Error cyka", err)
    else:
        ctx = Context(settings, db)
        uvloop.run(main(ctx))
