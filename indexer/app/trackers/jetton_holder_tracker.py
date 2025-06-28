from decimal import Decimal
from logging import getLogger
from typing import Optional

from tonsdk.boc import begin_cell, Cell
from tonsdk.utils import Address

from indexer.app.infra.ton import limiter
from indexer.app.infra.ton.api import list_jetton_holders
from indexer.app.trackers.base import BaseTracker
from libs.db.models import JettonWallet, DAOParticipant
from libs.db.ops import list_dao, insert_jetton_wallet, insert_dao_participant

logger = getLogger(__name__)


class JettonHolderTracker(BaseTracker):
    RETRY_DELAY = 60

    @property
    def name(self) -> str:
        return "jetton_holders"

    async def get_lock_address(self, dao: Address, owner: Address) -> Optional[Address]:
        cell = begin_cell().store_address(owner).end_cell()
        async with limiter:
            result = await self.ctx.tonapi_client.blockchain.execute_get_method(
                dao.to_string(), "get_lock_address", cell.to_boc().hex()
            )
        if not result.success:
            logger.error("Cannot fetch lock address %s", result)
            return None
        return (
            Cell.one_from_boc(bytes.fromhex(result.stack[0].cell))
            .begin_parse()
            .read_msg_addr()
        )

    async def run(self) -> None:
        logger.info("Run Jetton Holder Tracker")

        dao_list = await list_dao(self.ctx.db)

        for dao in dao_list:
            logger.debug("Fetching jetton holders for dao %s", dao.address.to_string())
            holders = await list_jetton_holders(self.ctx.tonapi_client, dao.jetton_master)

            for wallet in holders:
                while True:
                    owner = Address(wallet.owner.address.to_raw())
                    jetton_wallet = Address(wallet.address.to_raw())

                    logger.debug("Updating data for wallet %s", owner.to_string())

                    # Get lock address
                    lock_address = await self.get_lock_address(dao.address, owner)
                    await insert_dao_participant(self.ctx.db, DAOParticipant(
                        dao=dao.address,
                        address=owner,
                        jetton_wallet=jetton_wallet,
                        lock_address=lock_address,
                    ))

                    await insert_jetton_wallet(
                        self.ctx.db,
                        JettonWallet(
                            address=jetton_wallet,
                            owner=owner,
                            jetton_master=dao.jetton_master,
                            balance=Decimal(wallet.balance)
                        )
                    )
                    break
