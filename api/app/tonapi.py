from pytonapi import AsyncTonapi

from api.app.config import init_settings

tonapi_client = AsyncTonapi(init_settings().tonapi_token, is_testnet=init_settings().is_testnet)
