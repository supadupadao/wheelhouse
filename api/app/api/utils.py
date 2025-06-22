from typing import cast

from fastapi import Request
from pydantic import BaseModel
from tonsdk.utils import Address

from libs.db import Database


def get_db(request: Request) -> Database:
    return cast(Database, request.app.state.db)


class APIAddress(BaseModel):
    raw: str
    user_friendly: str

    @classmethod
    def from_address(cls, address: Address):
        return cls(
            raw=address.to_string(),
            user_friendly=address.to_string(is_user_friendly=True),
        )
