from fastapi import FastAPI

from api.app.api import router

app = FastAPI()

if __name__ == "__main__":
    app.include_router(router=router)
