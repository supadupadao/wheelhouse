from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import create_engine

from indexer.db.models import DAO, Wallet, Proposal, Vote, TraceLog
from indexer.error import IndexerDatabaseError


def init_db(db_url: str) -> Engine:
    try:
        engine = create_engine(db_url)

        # TODO FOR DEBUG. REMOVE LATER
        DAO.metadata.create_all(engine)
        Wallet.metadata.create_all(engine)
        Proposal.metadata.create_all(engine)
        Vote.metadata.create_all(engine)
        TraceLog.metadata.create_all(engine)
    except SQLAlchemyError as err:
        raise IndexerDatabaseError(err)
    else:
        return engine
