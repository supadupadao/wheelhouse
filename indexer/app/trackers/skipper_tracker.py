import asyncio
import logging

from indexer.app.infra.ton.api import list_new_traces, get_trace_info
from indexer.app.infra.ton.parsers.skipper import parse_skipper_trace, NewProposalState, VoteProposalState
from indexer.app.trackers.base import BaseTracker
from libs.db import DAO, TraceLog, Proposal
from libs.db.ops import list_dao, get_last_trace, insert_trace, insert_proposal
from libs.error import TonApiError, IndexerDataIsNotReady, BaseIndexerException

logger = logging.getLogger(__name__)


class SkipperTracker(BaseTracker):

    async def _track_trace(self, dao: DAO, trace_id: str):
        async with self.ctx.db.transaction():
            while True:
                try:
                    logger.info("Processing trace %s", trace_id)
                    trace_info = await get_trace_info(self.ctx.tonapi_client, trace_id)
                    logger.info("Trace info: %s", trace_info)
                    parsed_trace = await parse_skipper_trace(
                        dao.address,
                        self.ctx.tonapi_client,
                        trace_info
                    )
                except (TonApiError, IndexerDataIsNotReady) as err:
                    logger.error("Error processing trace %s: %s", trace_id, err)
                    await asyncio.sleep(self.RETRY_DELAY)
                except BaseIndexerException as err:
                    logger.error("Unexpected processing trace %s: %s", trace_id, err)
                    break
                else:
                    if isinstance(parsed_trace, NewProposalState) or isinstance(parsed_trace, VoteProposalState):
                        logger.info("Adding new proposal")
                        print("\n\n\nVOTES\n\n\n", parsed_trace.proposal_data.votes_yes,
                              parsed_trace.proposal_data.votes_no)
                        await insert_proposal(self.ctx.db, Proposal(
                            address=parsed_trace.address,
                            dao=dao.address,
                            id=parsed_trace.proposal_data.proposal_id,
                            is_initialized=parsed_trace.proposal_data.is_initialized,
                            is_executed=parsed_trace.proposal_data.is_executed,
                            votes_yes=parsed_trace.proposal_data.votes_yes,
                            votes_no=parsed_trace.proposal_data.votes_no,
                            expires_at=parsed_trace.proposal_data.expires_at,
                        ))

                    await insert_trace(self.ctx.db, TraceLog(
                        address=dao.address,
                        hash=trace_id,
                        utime=trace_info.transaction.utime
                    ))

                    break

    async def _track_dao(self, dao: DAO):
        logger.debug("Indexing dao %s", dao.address.to_string())

        while True:
            last_trace = await get_last_trace(self.ctx.db, dao.address)
            logger.debug("Last trace for dao %s is %s", dao.address.to_string(),
                         last_trace.hash if last_trace else None)
            try:
                traces = await list_new_traces(self.ctx.tonapi_client, last_trace, dao.address)
            except Exception as err:
                logger.error("Error fetching traces: %s", err)
                return

            if not traces:
                logger.debug("Empty traces list")
                return
            else:
                logger.info("There are %s new traces", len(traces))

            for trace_id in traces:
                await self._track_trace(dao, trace_id)

            return

    async def run(self) -> None:
        logger.info("Run Skipper Tracker")

        dao_list = await list_dao(self.ctx.db)

        for dao in dao_list:
            await self._track_dao(dao)
