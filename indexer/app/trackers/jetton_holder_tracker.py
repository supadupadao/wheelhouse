from logging import getLogger

from indexer.app.trackers.base import BaseTracker

logger = getLogger(__name__)


class JettonHolderTracker(BaseTracker):
    async def run(self) -> None:
        logger.info("Run Jetton Holder Tracker")
