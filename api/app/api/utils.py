from pydantic import BaseModel
from tonsdk.utils import Address


class APIAddress(BaseModel):
    raw: str
    user_friendly: str

    @classmethod
    def from_address(cls, address: Address):
        return cls(
            raw=address.to_string(),
            user_friendly=address.to_string(is_user_friendly=True),
        )

    @classmethod
    def parse_hash_part(cls, hash_part: bytes):
        hex = bytes.hex(hash_part)
        raw_addr = "0:" + hex
        ton_addr = Address(raw_addr)

        return cls.from_address(ton_addr)
