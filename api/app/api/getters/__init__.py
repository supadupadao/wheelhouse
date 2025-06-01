from fastapi import APIRouter

from .get_lock_address import router as get_lock_address_router
from .get_wallet_address import router as get_wallet_address_router

router = APIRouter(prefix="/getters")

router.include_router(get_lock_address_router)
router.include_router(get_wallet_address_router)
