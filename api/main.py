from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.app.api import router
from api.app.config import init_settings
from libs.db import Database


class AppState:
    db: Database


class CustomFastAPI(FastAPI):
    state: AppState


@asynccontextmanager
async def lifespan(application: CustomFastAPI):
    db = Database(init_settings().DB_URL)
    await db.connect()

    application.state = AppState()
    application.state.db = db

    yield
    await db.close()


app = CustomFastAPI(
    title="SupaDupaDAO API",
    description="Public API of Skipper contract indexers",
    lifespan=lifespan,
)

app.include_router(router=router)
