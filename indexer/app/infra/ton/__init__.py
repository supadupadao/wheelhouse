from aiolimiter import AsyncLimiter
from pytonapi import AsyncTonapi

limiter = AsyncLimiter(max_rate=1, time_period=1.5)


def init_tonapi_client(tonapi_token: str, is_testnet: bool) -> AsyncTonapi:
    return AsyncTonapi(tonapi_token, is_testnet=is_testnet)
