from fastapi import APIRouter

from .proposals import router as proposals_router

router = APIRouter(prefix="/api")

router.include_router(proposals_router)

__all__ = ["router"]
