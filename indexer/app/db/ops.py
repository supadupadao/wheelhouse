from typing import Optional

from sqlalchemy import Engine, Select
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from tonsdk.utils import Address

from libs.db import address_into_db_format, DAO, TraceLog, Proposal


def get_or_create_dao(engine: Engine, dao_address: Address) -> DAO:
    dao_address = address_into_db_format(dao_address)
    with Session(engine) as session:
        result = session.get(DAO, {
            "address": dao_address
        })
        if result is None:
            result = DAO(address=dao_address)
            session.add(result)
            session.commit()
            session.refresh(result)
        return result


def get_last_trace(engine: Engine, dao: DAO) -> Optional[TraceLog]:
    with Session(engine) as session:
        query: Select = select(TraceLog).where(TraceLog.dao == dao.address).order_by(-TraceLog.utime).limit(1)
        return session.exec(query).first()


def insert_trace(engine: Engine, trace: TraceLog):
    with Session(engine) as session:
        session.add(trace)
        try:
            session.commit()
        except IntegrityError:
            pass


def insert_proposal(engine: Engine, proposal: Proposal):
    with Session(engine) as session:
        session.add(proposal)
        try:
            session.commit()
        except IntegrityError:
            pass
