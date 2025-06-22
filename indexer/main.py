import asyncio
import logging

import uvloop

from indexer.app.common.ctx import Context
from indexer.app.config import init_settings
from indexer.app.infra.ton import init_tonapi_client
from indexer.app.logging_config import init_logging
from indexer.app.trackers.base import BaseTracker
from indexer.app.trackers.jetton_holder_tracker import JettonHolderTracker
from indexer.app.trackers.minter_tracker import MinterTracker
from indexer.app.trackers.skipper_tracker import SkipperTracker
from libs.db import Database
from libs.db.migrations import run_migrations
from libs.error import BaseIndexerException

logger = logging.getLogger(__name__)


async def run_tracker_loop(tracker: BaseTracker):
    while True:
        # TODO add exception handler
        await tracker.run()
        logger.debug("Rerun tracker iteration in %s", tracker.RETRY_DELAY)
        await asyncio.sleep(tracker.RETRY_DELAY)


async def main(context: Context):
    logger.info("Connecting to Database")
    await context.db.connect()
    logger.info("Running migrations")
    await run_migrations(context.db, path="../migrations")

    trackers = [
        MinterTracker(ctx),
        SkipperTracker(ctx),
        JettonHolderTracker(ctx),
    ]

    await asyncio.gather(*(run_tracker_loop(t) for t in trackers))


if __name__ == "__main__":
    # Initialize config
    try:
        settings = init_settings()

        init_logging(settings.log_level)

        db = Database(settings.db_url)
        tonapi_client = init_tonapi_client(settings.tonapi_token, settings.is_testnet)
    except BaseIndexerException as err:
        logger.error("Initialization error: %s", err)
    else:
        ctx = Context(settings, db, tonapi_client)
        logger.info("Indexer started")
        uvloop.run(main(ctx))
