from tonsdk.utils import Address


def address_into_db_format(address: Address) -> bytes:
    return bytes(address.hash_part)


def str_to_address(address: str) -> Address:
    return Address(address)
