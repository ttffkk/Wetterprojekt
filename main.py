from fastapi import FastAPI
from web import routers

app = FastAPI()

app.include_router(routers.router)
