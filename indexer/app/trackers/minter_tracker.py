import asyncio
import logging

from tonsdk.utils import Address

from indexer.app.common.ctx import Context
from indexer.app.infra.ton.api import list_new_traces, get_trace_info
from indexer.app.infra.ton.parsers.minter import parse_minter_trace, DeployDAOState
from indexer.app.trackers.base import BaseTracker
from libs.db import TraceLog, DAO
from libs.db.ops import get_last_trace, insert_trace, insert_dao
from libs.db.utils import str_to_address
from libs.error import TonApiError, IndexerDataIsNotReady, BaseIndexerException

logger = logging.getLogger(__name__)


class MinterTracker(BaseTracker):
    RETRY_DELAY = 120
    minter_address: Address

    @property
    def name(self) -> str:
        return "minter"

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.minter_address = str_to_address(ctx.cfg.SKIPPER_MINTER_ADDRESS)

    async def run(self) -> None:
        logger.info("Run Minter Tracker")

        last_trace = await get_last_trace(self.ctx.db, self.minter_address)
        logger.debug(
            "Last trace for minter is %s", last_trace.hash if last_trace else None
        )
        try:
            traces = await list_new_traces(
                self.ctx.tonapi_client, last_trace, self.minter_address
            )
        except Exception as err:
            logger.error("Error fetching traces: %s", err)
            return

        if not traces:
            logger.debug("Empty traces list")
            return
        else:
            logger.info("There are %s new traces", len(traces))

        for trace_id in traces:
            async with self.ctx.db.transaction():
                while True:
                    try:
                        logger.info("Processing trace %s", trace_id)
                        trace_info = await get_trace_info(
                            self.ctx.tonapi_client, trace_id
                        )
                        logger.info("Trace info: %s", trace_info)
                        parsed_trace = await parse_minter_trace(
                            self.minter_address, self.ctx.tonapi_client, trace_info
                        )
                    except (TonApiError, IndexerDataIsNotReady) as err:
                        logger.error("Error processing trace %s: %s", trace_id, err)
                        await asyncio.sleep(self.RETRY_DELAY)
                    except BaseIndexerException as err:
                        logger.error(
                            "Unexpected processing trace %s: %s", trace_id, err
                        )
                        break
                    else:
                        if isinstance(parsed_trace, DeployDAOState):
                            logger.info("Registering new DAO")
                            await insert_dao(
                                self.ctx.db,
                                DAO(
                                    address=parsed_trace.address,
                                    jetton_master=parsed_trace.jetton_master,
                                    jetton_name=parsed_trace.jetton_name,
                                    jetton_symbol=parsed_trace.jetton_symbol,
                                    jetton_description=parsed_trace.jetton_description,
                                    jetton_icon_url=parsed_trace.jetton_icon_url,
                                ),
                            )

                        await insert_trace(
                            self.ctx.db,
                            TraceLog(
                                address=self.minter_address,
                                hash=trace_id,
                                utime=trace_info.transaction.utime,
                            ),
                        )

                        break
