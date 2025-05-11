from fastapi import FastAPI

from api.app.api import router

app = FastAPI()

app.include_router(router=router)
