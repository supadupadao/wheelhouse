from aiolimiter import AsyncLimiter
from pytonapi import AsyncTonapi

from api.app.config import init_settings

limiter = AsyncLimiter(max_rate=1, time_period=1.5)

tonapi_client = AsyncTonapi(init_settings().tonapi_token, is_testnet=init_settings().is_testnet)
