from tonsdk.utils import Address


def address_into_db_format(address: Address) -> bytes:
    return bytes(address.hash_part)
