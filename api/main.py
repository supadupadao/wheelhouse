from fastapi import FastAPI

from api.app.api import router
from api.app.config import init_settings
from libs.db import init_db

settings = init_settings()
engine = init_db(settings.db_url)
app = FastAPI()

app.include_router(router=router)
