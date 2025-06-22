from tonsdk.utils import Address


def address_into_db_format(address: Address) -> bytes:
    return bytes(address.hash_part)


def address_from_db_format(hash_part: bytes) -> Address:
    hex_str = bytes.hex(hash_part)
    raw_addr = "0:" + hex_str
    return Address(raw_addr)


def str_to_address(address: str) -> Address:
    return Address(address)
