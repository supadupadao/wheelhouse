from fastapi import APIRouter

from . import getters
from .dao import router as dao_router
from .proposals import router as proposals_router

router = APIRouter(prefix="/api")

router.include_router(proposals_router)
router.include_router(dao.router)
router.include_router(getters.router)

__all__ = ["router"]
