import logging

import uvloop

from indexer.app.common.ctx import Context
from indexer.app.config import init_settings
from indexer.app.db.ops import get_or_create_dao, get_last_trace
from indexer.app.error import BaseIndexerException
from indexer.app.logging_config import init_logging
from indexer.app.ton import init_tonapi_client
from indexer.app.ton.api import list_new_traces, get_trace_info
from indexer.app.ton.parser import parse_trace
from indexer.app.ton.utils import str_to_address
from libs.db import init_db


async def main(context: Context):
    dao_address = str_to_address(context.cfg.skipper_address)
    raw_dao_address = dao_address.to_string(is_user_friendly=False)

    tonapi_client = init_tonapi_client(context.cfg.tonapi_token, context.cfg.is_testnet)
    logging.info("TONAPI client initialized")

    dao_record = get_or_create_dao(context.db, dao_address)

    last_indexed_trace = get_last_trace(context.db, dao_record)
    logging.info("Last indexed trace %s", last_indexed_trace)
    while True:
        traces = await list_new_traces(tonapi_client, last_indexed_trace, dao_address.to_string())
        logging.info("Fetched traces: %s", traces)
        for trace_id in traces:
            logging.info("Processing trace %s", trace_id)
            trace_info = await get_trace_info(tonapi_client, trace_id)
            logging.info("Trace info: %s", trace_info)
            parsed_trace = await parse_trace(raw_dao_address, tonapi_client, trace_info)


if __name__ == "__main__":
    # Initialize config
    try:
        settings = init_settings()

        init_logging(settings.log_level)

        db = init_db(settings.db_url)
    except BaseIndexerException as err:
        logging.error("Initialization error: %s", err)
    else:
        ctx = Context(settings, db)
        logging.info("Indexer started")
        uvloop.run(main(ctx))
