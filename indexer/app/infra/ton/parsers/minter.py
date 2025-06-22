import logging
from dataclasses import dataclass, asdict

from pytonapi import AsyncTonapi
from pytonapi.schema.traces import Trace
from tonsdk.boc import Cell
from tonsdk.utils import Address

from indexer.app.infra.ton import limiter
from indexer.app.infra.ton.parsers import BaseState, traverse_children, S
from libs.db.utils import str_to_address
from libs.error import IndexerDataIsNotReady, TonApiError

logger = logging.getLogger(__name__)


@dataclass
class MinterState(BaseState):
    minter_address: Address


@dataclass
class DeployDAOState(MinterState):
    address: Address
    jetton_master: Address


async def parse_minter_trace(
        minter_address: Address, tonapi_client: AsyncTonapi, trace_info: Trace
):
    state = MinterState(minter_address=minter_address, tonapi_client=tonapi_client)

    return await traverse_children(state, trace_info.children or [], find_minter)


async def find_minter(state: S, trace: Trace):
    if len(trace.transaction.out_msgs) > 0:
        raise IndexerDataIsNotReady("Transaction is not executed yet")

    if trace.transaction.account.address.to_raw() == state.minter_address.to_string(is_user_friendly=False):
        opcode = int(trace.transaction.in_msg.op_code, 16)

        if opcode == 0x690001:
            return await traverse_children(
                state, trace.children, handle_dao_deploy
            )

    if trace.children is not None:
        logger.info("Parsing children")
        return await traverse_children(state, trace.children, find_minter)
    return None


async def handle_dao_deploy(state: S, trace: Trace):
    dao_contract = trace.transaction.account.address.to_raw()
    # return DeployDAOState()
    async with limiter:
        result = await state.tonapi_client.blockchain.execute_get_method(
            dao_contract, "get_jetton_master"
        )
    if result.success:
        jetton_master = (
            Cell.one_from_boc(bytes.fromhex(result.stack[0].cell))
            .begin_parse()
            .read_msg_addr()
        )

        return DeployDAOState(
            address=str_to_address(dao_contract),
            jetton_master=jetton_master,
            **asdict(state)
        )
    else:
        raise TonApiError("Error fetching proposal state")
